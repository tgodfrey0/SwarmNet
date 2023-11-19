import socket
import queue
from typing import List, Tuple, Callable

import swarmnet.logger as logger

log = logger.Logger("broadcaster")

class Broadcaster:
  def __init__(self, port: int, rx: queue.Queue):
    self.addr = "192.168.0.255"
    self.port = port
    self.rx = rx
    
    self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.listener.bind((self.addr, self.port))
    self.listener.settimeout(5)
    
    log.success("SwarmNet broadcaster started")
    
  def broadcast(self, msg: str) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(bytes(msg, "utf-8"),('255.255.255.255', self.port))
    sock.close()
    log.info(f"Broadcast message {msg} sent")
    
  def listen_broadcast(self) -> None:
    try:
      msg = self.listener.recvfrom(1024)
    except TimeoutError:
      return
    
    log.info(f"Broadcast received")

    parts = msg.split(":", 1)
    if not self.received(parts[0]):
      self.rx.put(parts[1])
      self.register_received(parts[0])
