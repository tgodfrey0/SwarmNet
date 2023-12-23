import threading
import socket
import queue
from typing import Callable, Optional, List, Dict, Tuple
import time

from . import logger
from . import broadcaster
from . import msg_parser
from . import receiver
from . import sender

log = logger.Logger("controller")

class SwarmNet:
  
  """!
  @brief SwarmNet controller constructor
  
  @param mapping A mapping of command token to parsing function
  @param port The communication port (defaults to 51000)
  @param device_list A static device list of (IP, Port) (If not provided device discovery will be used) 
  """
  def __init__(self, 
               mapping: Dict[str, Callable[[Optional[str]], None]], 
              #  device_retries: int = 3, 
              #  device_refresh_interval: int = 60,
               port: int = 51000,
               device_list: List[Tuple[str, int]] = []):
    self.fn_map = mapping
    # self.discovery_retries = device_retries
    # self.discovery_interval = device_refresh_interval
    self.port = port
    
    if(device_list != []):
      self.fixed_list = True
      self.swarm_list: List[Tuple[str, int]] = device_list
      log.info("Static device list provided")
    else:
      self.fixed_list = False
      self.swarm_list: List[Tuple[str, int]] = []
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 1))
    self.addr = s.getsockname()[0]
    s.close()
    
    log.info(f"This address is {self.addr}:{self.port}")
    
    log.success("SwarmNet controller started")
  
  """!
  @brief Starts the required threads
  """  
  def start(self) -> None:
    self.swarm_list_lock = threading.Lock()
    self.received_ids = []
    self.received_ids_lock = threading.Lock()
    self.rx_queue = queue.Queue(128)
    self.tx_queue = queue.Queue(32)
    self.fn_map["JOIN"] = self._register_new_member
    self.parser = msg_parser.MessageParser(self.fn_map, self.rx_queue)
    self.receiver = receiver.Receiver(self.addr, self.port, self.add_device, self._has_seen_message, self._append_seen_messages, rx_queue=self.rx_queue, tx_queue=self.tx_queue)
    self.sender = sender.Sender(self.addr, self.tx_queue, self.remove_device)
    self.broadcaster = broadcaster.Broadcaster(self.addr, self.port, self.rx_queue, self.add_device, self.fixed_list, self.swarm_list)
    
    self.parse_thread = threading.Thread(target=_parse_thread_target, args=[self])
    self.parse_thread_exit_request = False
    self.parse_thread.start()
    log.info("Parser thread started")
    
    self.receiver_thread = threading.Thread(target=_receiver_thread_target, args=[self])
    self.receiver_thread_exit_request = False
    self.receiver_thread.start()
    log.info("Receiver thread started")
    
    self.sender_thread = threading.Thread(target=_sender_thread_target, args=[self])
    self.sender_thread_exit_request = False
    self.sender_thread.start()
    log.info("Sender thread started")
    
    log.info_header("Beginning broadcast of JOIN command")
    self.broadcast(f"JOIN {self.addr} {self.port}")
    
  """!
  @brief Kills all threads in a safe way
  """
  def kill(self) -> None:
    self.broadcaster_thread_exit_request = True
    self.parse_thread_exit_request = True
    self.receiver_thread_exit_request = True
    self.sender_thread_exit_request = True
    
    self.parse_thread.join()
    self.receiver_thread.join()
    self.sender_thread.join()
    
    log.warn("All threads have been killed")
  
  """!
  @brief Clears all messages waiting to be parsed
  """
  def clear_rx_queue(self):
    with self.rx_queue.mutex:
      self.rx_queue.queue.clear()
      
  """!
  @brief Clears all messages waiting to be sent
  """
  def clear_tx_queue(self):
    with self.tx_queue.mutex:
      self.tx_queue.queue.clear()
    
  def _register_new_member(self, msg: Optional[str]) -> None:
    addr = msg.split(" ", 1)[0]
    port = msg.split(" ", 1)[1]
    self.add_device((addr, int(port)))
      
  """!
  @brief Get the list of connected devices
  
  @returns A list of devices
  """
  def get_devices(self) -> List[Tuple[str, int]]:
    self.swarm_list_lock.acquire()
    ds = self.swarm_list
    self.swarm_list_lock.release()
    return ds
  
  """!
  @brief Set the list of connected devices
  
  This does not work if dynamic device discovery is disabled
  
  @param ds The list of devices in the form of (IP, Port)
  """
  def set_devices(self, ds: List[Tuple[str, int]]) -> None:
    if(self.fixed_list):
      return
    
    self.swarm_list_lock.acquire()
    self.swarm_list = ds
    self.swarm_list_lock.release()
  
  """!
  @brief Append a device to the list of connected devices
  
  This does not work if dynamic device discovery is disabled
  
  @param d The device (IP, Port)
  """
  def add_device(self, d: Tuple[str, int]) -> None:
    if(self.fixed_list):
      return
    
    if(d[0] == self.addr):
      return
    self.swarm_list_lock.acquire()
    
    if(d in self.swarm_list):
      return
    
    self.swarm_list.append(d)
    self.swarm_list_lock.release()
    log.info(f"New device added at {d[0]}:{d[1]}")
  
  """!
  @brief Remove a device from the list of connected devices
  
  This does not work if dynamic device discovery is disabled
  
  @param d The device to remove in the form (IP, Port)
  """
  def remove_device(self, d: Tuple[str, int]) -> None:
    if(self.fixed_list):
      return
    
    self.swarm_list_lock.acquire()
    self.swarm_list.remove(d)
    self.swarm_list_lock.release()
    log.warn(f"Device removed at {d[0]}:{d[1]}")
  
  def _get_seen_messages(self) -> List[str]:
    self.received_ids_lock.acquire()
    ms = self.received_ids
    self.received_ids_lock.release()
    return ms
  
  def _set_seen_messages(self, ms: List[str]) -> None:
    self.received_ids_lock.acquire()
    self.received_ids = ms
    self.received_ids_lock.release()
  
  def _append_seen_messages(self, m: str) -> None:
    self.received_ids_lock.acquire()
    self.received_ids.append(m)
    self.received_ids_lock.release()
    
  def _has_seen_message(self, m: str) -> bool:
    self.received_ids_lock.acquire()
    b = m in self.received_ids
    self.received_ids_lock.release()
    return b
  
  """!
  @brief Set the logging level
  
  @param lv The minimum log level to output
  """
  def set_log_level(lv: logger.Logger.Log_Level) -> None:
    log.set_log_level(lv)
    
  def _calc_header(self) -> str:
    return f"{time.time()}/{self.addr}/{self.port}"
  
  """!
  @brief Send a message
  
  @param msg The message to send
  """
  def send(self, msg: str):
    header = self._calc_header()
    self._append_seen_messages(header)
    self.tx_queue.put(f"{header}:{msg}", block=True)
  
  """!
  @brief Broadcast a message to all IPs in the subnet
  
  If a static device list is provided, this is no different to the `send` method
  
  @param The message to send
  """  
  def broadcast(self, msg: str):
    header = self._calc_header()
    self._append_seen_messages(header)
    self.broadcaster.broadcast(f"{header}:{msg}")
    
def _parse_thread_target(ctrl: SwarmNet):
  while(not ctrl.parse_thread_exit_request):
    if not ctrl.rx_queue.empty():
      ctrl.parser.parse_msg()
    else:
      time.sleep(0.01)
  log.warn("Parse thread killed")
    
def _receiver_thread_target(ctrl: SwarmNet):
  while(not ctrl.receiver_thread_exit_request):
    ctrl.receiver.accept_connection()
  log.warn("Receiver thread killed")

def _sender_thread_target(ctrl: SwarmNet):
  while(not ctrl.sender_thread_exit_request):
    if not ctrl.tx_queue.empty():
      ctrl.sender.flush_queue(ctrl.get_devices())
    else:
      time.sleep(0.01)
  log.warn("Sender thread killed") 
    
