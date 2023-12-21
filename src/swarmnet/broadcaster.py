import socket
import queue
import threading
from typing import Callable, Tuple, List

from . import logger

log = logger.Logger("broadcaster")

TIMEOUT = 0.5

class Broadcaster:
  def __init__(self, self_addr: str, port: int, rx: queue.Queue, add_device_fn: Callable[[Tuple[str, int]], None], fixed_list: bool, devices: List[Tuple[str, int]]):
    self.self_addr = self_addr
    self.port = port
    self.rx = rx
    self.add_device = add_device_fn
    self.fixed_list = fixed_list
    
    if(fixed_list):
      self.device_list = devices
    
    log.success("SwarmNet broadcaster started")
    
  def broadcast(self, msg: str) -> None:
    if(self.fixed_list):
      self._bc_static_list(msg)
    else:
      lower = threading.Thread(target=self._bc_lower, args=[msg])
      upper = threading.Thread(target=self._bc_upper, args=[msg])
      
      lower.start()
      upper.start()
      
      lower.join()
      upper.join()
        
    log.success(f"Broadcast message {msg} sent")
    
  def _bc_static_list(self, msg) -> None:
    for ap in self.device_list:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        try:
          sock.connect(ap)
          sock.send(bytes(msg + "\n", "utf-8"))
        except OSError:
          pass
        sock.close()
    
  def _bc_lower(self, msg) -> None:
    for addr_end in range(2,128):
        if(str(addr_end) == self.self_addr.split(".")[3]):
          continue
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        try:
          sock.connect((f"192.168.0.{addr_end}", self.port))
          sock.send(bytes(msg + "\n", "utf-8"))
          self.add_device((f"192.168.0.{addr_end}", self.port))
        except OSError:
          pass
        sock.close()
    
  def _bc_upper(self, msg) -> None:
    for addr_end in range(128,255):
        if(str(addr_end) == self.self_addr.split(".")[3]):
          continue
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        try:
          sock.connect((f"192.168.0.{addr_end}", self.port))
          sock.send(bytes(msg + "\n", "utf-8"))
          self.add_device((f"192.168.0.{addr_end}", self.port))
        except OSError:
          pass
        sock.close()

