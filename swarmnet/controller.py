import threading
import socket
import queue
from typing import Callable, Optional, List
import time
import math

import swarmnet.logger as logger
import swarmnet.discovery as discovery
import swarmnet.parser as parser
import swarmnet.receiver as receiver
import swarmnet.sender as sender

log = logger.Logger("controller")

class SwarmNet:
  def __init__(self, 
               mapping: {str: Callable[[Optional[str]], None]}, 
               device_retries: int = 3, 
               device_refresh_interval: int = 60,
               port: int = 9999):
    self.fn_map = mapping
    self.discovery_retries = device_retries
    self.discovery_interval = device_refresh_interval
    self.port = port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))
    self.addr = s.getsockname()[0]
    s.close()
    log.info(f"This address is {self.addr}:{self.port}")
    
    log.success("SwarmNet controller started")
    
  def start(self) -> None:
    self.swarm_list = []
    self.swarm_list_lock = threading.Lock()
    self.received_ids = []
    self.received_ids_lock = threading.Lock()
    self.rx_queue = queue.Queue(128)
    self.tx_queue = queue.Queue(32)
    self.parser = parser.Parser(self.fn_map, self.rx_queue)
    self.receiver = receiver.Receiver(self.addr, self.port, self.has_seen_message, self.append_seen_messages, rx_queue=self.rx_queue, tx_queue=self.tx_queue)
    self.sender = sender.Sender(self.addr, self.port, self.tx_queue)
    
    # self.discovery_thread = threading.Thread(target=discovery_thread_target, args=[self])
    # self.discovery_thread_exit_request = False
    # self.discovery_thread.start()
    # log.info("Discovery thread started")
    
    self.parse_thread = threading.Thread(target=parse_thread_target, args=[self])
    self.parse_thread_exit_request = False
    self.parse_thread.start()
    log.info("Parser thread started")
    
    self.receiver_thread = threading.Thread(target=receiver_thread_target, args=[self])
    self.receiver_thread_exit_request = False
    self.receiver_thread.start()
    log.info("Receiver thread started")
    
    self.sender_thread = threading.Thread(target=sender_thread_target, args=[self])
    self.sender_thread_exit_request = False
    self.sender_thread.start()
    log.info("Sender thread started")
    
  def kill(self) -> None:
    self.discovery_thread_exit_request = True
    self.parse_thread_exit_request = True
    self.receiver_thread_exit_request = True
    self.sender_thread_exit_request = True
    
    # self.discovery_thread.join()
    self.parse_thread.join()
    self.receiver_thread.join()
    self.sender_thread.join()
    
    log.warn("All threads have been killed")
  
  def _update_device_list(self) -> None:
    for _ in range(0, self.discovery_retries):
      ds = discovery.discover_swarm_devices()
      if ds != {}:
        self.set_devices(ds)
        return;
      log.info("Retrying swarm discovery")
    
    log.error(f"Retry limit ({self.discovery_retries}) reached during swarm discovery")
      
  def get_devices(self) -> List[str]:
    self.swarm_list_lock.acquire()
    ds = self.swarm_list
    self.swarm_list_lock.release()
    return ds
  
  def set_devices(self, ds: List[str]) -> None:
    self.swarm_list_lock.acquire()
    self.swarm_list = ds
    self.swarm_list_lock.release()
    
  def get_seen_messages(self) -> List[str]:
    self.received_ids_lock.acquire()
    ms = self.received_ids
    self.received_ids_lock.release()
    return ms
  
  def set_seen_messages(self, ms: List[str]) -> None:
    self.received_ids_lock.acquire()
    self.received_ids = ms
    self.received_ids_lock.release()
  
  def append_seen_messages(self, m: str) -> None:
    self.received_ids_lock.acquire()
    self.received_ids.append(m)
    self.received_ids_lock.release()
    
  def has_seen_message(self, m: str) -> bool:
    self.received_ids_lock.acquire()
    b = m in self.received_ids
    self.received_ids_lock.release()
    return b
  
  def set_log_level(lv: logger.Logger.Log_Level) -> None:
    log.set_log_level(lv)
    
  def send(self, msg: str):
    header = f"{time.time()}/{self.addr}"
    self.append_seen_messages(header)
    self.tx_queue.put(f"{header}:{msg}", block=True)
    
def parse_thread_target(ctrl: SwarmNet):
  while(not ctrl.parse_thread_exit_request):
    if not ctrl.rx_queue.empty:
      ctrl.parser.parse_msg()
    else:
      time.sleep(0.01)
  log.warn("Parse thread killed")
    
def receiver_thread_target(ctrl: SwarmNet):
  while(not ctrl.receiver_thread_exit_request):
    ctrl.receiver.control_receiver(ctrl.receiver_thread_exit_request)
  log.warn("Receiver thread killed")
    
def sender_thread_target(ctrl: SwarmNet):
  while(not ctrl.sender_thread_exit_request):
    if not ctrl.tx_queue.empty():
      print("IN IF")
      ctrl.sender.flush_queue(ctrl.get_devices())
    else:
      time.sleep(0.01)
  log.warn("Sender thread killed") 
    
def discovery_thread_target(ctrl: SwarmNet):
  while(1):
    # Update every 60 seconds
    if not ctrl.discovery_thread_exit_request:
      t0 = time.time()
      ctrl._update_device_list()
      t1 = time.time()
    elif not ctrl.discovery_thread_exit_request:
      time.sleep(ctrl.discovery_interval - (t1 - t0))
    else:
      break
  log.warn("Discovery thread killed")