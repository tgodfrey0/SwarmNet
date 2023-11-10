import threading
import bluetooth
import queue
from typing import Callable, Optional
import time

import swarmnet.logger as logger
import swarmnet.discovery as discovery
import swarmnet.parser as parser

log = logger.Logger("controller")

class SwarmNet:
  def __init__(self, pref: str, mapping: {str: Callable[[Optional[str]], None]}, bt_device_retries: int = 3, bt_device_refresh_interval: int = 60):
    self.swarm_prefix = pref
    self.fn_map = mapping
    self.discovery_retries = bt_device_retries
    self.discovery_interval = bt_device_refresh_interval
    
    log.success("SwarmNet controller successfully created")
    
  def start(self) -> None:
    self.devices_lock = threading.Lock()
    self.swarm_list = {}
    self.messages = queue.Queue()
    self.parser = parser.Parser(self.fn_map, self.messages)
    
    discovery_thread = threading.Thread(target=discovery_thread_target, args=[self])
    discovery_thread.start()
    log.info("Discovery thread started")
    
    parse_thread = threading.Thread(target=parse_thread_target, args=[self])
    parse_thread.start()
    log.info("Parser thread started")
    
    #receive_thread
  
  def _update_device_list(self) -> None:
    for i in range(0, self.discovery_retries):
      ds = discovery.discover_swarm_devices(self.swarm_prefix)
      if ds != {}:
        self.set_devices(ds)
        return;
      log.info("Retrying swarm discovery")
    
    log.error(f"Retry limit ({self.discovery_retries}) reached during swarm discovery")
      
  def get_devices(self) -> {str: str}:
    self.devices_lock.acquire()
    ds = self.swarm_list
    self.devices_lock.release()
    return ds
  
  def set_devices(self, ds: {str: str}) -> None:
    self.devices_lock.acquire()
    self.swarm_list = ds
    self.devices_lock.release()
  
  def set_log_level(lv: logger.Logger.Log_Level) -> None:
    log.set_log_level(lv)
    
def parse_thread_target(ctrl: SwarmNet):
  while(1):
    ctrl.parser.parse_msg()
    
def discovery_thread_target(ctrl: SwarmNet):
  while(1):
    # Update every 60 seconds
    t0 = time.time()
    ctrl._update_device_list()
    t1 = time.time()
    time.sleep(ctrl.discovery_interval - (t1 - t0))