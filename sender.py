import socket
import queue
from typing import List, Tuple, Callable

from . import logger

log = logger.Logger("sender")

class Sender:
  def __init__(self, self_addr: str, tx_queue: queue.Queue, remove_device_fn: Callable[[Tuple[str, int]], None]):
    self.tx = tx_queue
    self.self_addr = self_addr
    self.remove_dev = remove_device_fn
    log.success("SwarmNet sender started")
    
  def flush_queue(self, devices: List[Tuple[str, int]]):
    while(not self.tx.empty()):
      msg = self.tx.get()
      log.info(f"Sending message: {msg}")
      for (addr, port) in devices:
        if(addr == self.self_addr.split(".")[3]):
          continue
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        try:
          sock.connect((addr, port))
          sock.send(bytes(msg + "\n", "utf-8"))
        except OSError:
          self.remove_dev((addr, port))
          raise
        sock.close()
      log.success("Message sent to all swarm devices")
