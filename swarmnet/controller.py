import threading
import socket
import queue
from typing import Callable, Optional, List, Dict, Tuple
import time
import math

import swarmnet.logger as logger
import swarmnet.broadcaster as broadcaster
import swarmnet.parser as parser
import swarmnet.receiver as receiver
import swarmnet.sender as sender

log = logger.Logger("controller")

class SwarmNet:
  def __init__(self, 
               mapping: Dict[str, Callable[[Optional[str]], None]], 
               device_retries: int = 3, 
               device_refresh_interval: int = 60,
               port: int = 51000,
               broadcast_port: int = 51001):
    self.fn_map = mapping
    self.discovery_retries = device_retries
    self.discovery_interval = device_refresh_interval
    self.port = port
    self.broadcast_port = broadcast_port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))
    self.addr = s.getsockname()[0]
    s.close()
    log.info(f"This address is {self.addr}:{self.port}")
    
    log.success("SwarmNet controller started")
    
  def start(self) -> None:
    self.swarm_list: List[Tuple[str, str]] = []
    self.swarm_list_lock = threading.Lock()
    self.received_ids = []
    self.received_ids_lock = threading.Lock()
    self.rx_queue = queue.Queue(128)
    self.tx_queue = queue.Queue(32)
    self.fn_map["JOIN"] = self._register_new_member
    self.parser = parser.Parser(self.fn_map, self.rx_queue)
    self.receiver = receiver.Receiver(self.addr, self.port, self.has_seen_message, self.append_seen_messages, rx_queue=self.rx_queue, tx_queue=self.tx_queue)
    self.sender = sender.Sender(self.addr, self.tx_queue, self.remove_device)
    self.broadcaster = broadcaster.Broadcaster(self.broadcast_port, self.add_device)
    
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
    
    self.broadcaster_thread = threading.Thread(target=broadcaster_thread_target, args=[self])
    self.broadcaster_thread_exit_request = False
    self.broadcaster_thread.start()
    log.info("Broadcaster thread started")
    
    self.broadcast(f"JOIN {self.addr} {self.port}")
    
  def kill(self) -> None:
    self.broadcaster_thread_exit_request = True
    self.parse_thread_exit_request = True
    self.receiver_thread_exit_request = True
    self.sender_thread_exit_request = True
    
    self.parse_thread.join()
    self.receiver_thread.join()
    self.sender_thread.join()
    self.broadcaster_thread.join
    
    log.warn("All threads have been killed")
    
  def _register_new_member(self, msg: Optional[str]) -> None:
    addr = msg.split(" ", 1)[0]
    port = msg.split(" ", 1)[0]
    self.add_device((addr, port))
      
  def get_devices(self) -> List[Tuple[str, str]]:
    self.swarm_list_lock.acquire()
    ds = self.swarm_list
    self.swarm_list_lock.release()
    return ds
  
  def set_devices(self, ds: List[Tuple[str, str]]) -> None:
    self.swarm_list_lock.acquire()
    self.swarm_list = ds
    self.swarm_list_lock.release()
    
  def add_device(self, d: Tuple[str, str]) -> None:
    self.swarm_list_lock.acquire()
    self.swarm_list.append(d)
    self.swarm_list_lock.release()
    logger.info(f"New device added at {d[0]}:{d[1]}")
    
  def remove_device(self, d: Tuple[str, str]) -> None:
    self.swarm_list_lock.acquire()
    self.swarm_list.remove(d)
    self.swarm_list_lock.release()
    logger.warn(f"Device removed at {d[0]}:{d[1]}")
    
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
    
  def broadcast(self, msg: str):
    header = f"{time.time()}/{self.addr}"
    self.append_seen_messages(header)
    self.broadcaster.broadcast(f"{header}:{msg}")
    
def parse_thread_target(ctrl: SwarmNet):
  while(not ctrl.parse_thread_exit_request):
    if not ctrl.rx_queue.empty():
      ctrl.parser.parse_msg()
    else:
      time.sleep(0.01)
  log.warn("Parse thread killed")
    
def receiver_thread_target(ctrl: SwarmNet):
  while(not ctrl.receiver_thread_exit_request):
    ctrl.receiver.accept_connection()
  log.warn("Receiver thread killed")
  
def broadcaster_thread_target(ctrl: SwarmNet):
  while(not ctrl.broadcaster_thread_exit_request):
    ctrl.broadcaster.listen_broadcast()
  log.warn("Broadcaster thread killed")
    
def sender_thread_target(ctrl: SwarmNet):
  while(not ctrl.sender_thread_exit_request):
    if not ctrl.tx_queue.empty():
      ctrl.sender.flush_queue(ctrl.get_devices())
    else:
      time.sleep(0.01)
  log.warn("Sender thread killed") 
    
