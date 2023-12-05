import queue
import socket
from typing import Callable, Tuple

from . import logger

log = logger.Logger("receiver")

class Receiver:
  def __init__(self, addr: str, port: int, add_device: Callable[[Tuple[str, int]], None], received: Callable[[str], bool], register_received: Callable[[str], None], rx_queue: queue.Queue, tx_queue: queue.Queue):
    self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.listener.bind((addr, port))
    self.listener.listen()
    self.listener.settimeout(5)
    self.add_device = add_device
    self.received = received
    self.register_received = register_received
    self.rx = rx_queue
    self.tx = tx_queue
  
    log.info("Waiting for connections")
    log.success("SwarmNet receiver started")
    
  def control_receiver(self, exit_request: bool) -> None:
    if(exit_request):
      self.listener.shutdown()
    
  def accept_connection(self) -> None:
    try:
      client_sock, client_info = self.listener.accept()
    except TimeoutError:
      return
    
    log.info(f"Connection received")

    full_data: str = ""
    try:
      while True:
        data = client_sock.recv(1024)
        if not data:
          break
        full_data += data.decode("utf-8")
    except OSError:
      pass
    
    #TODO: Add new devices to list
    parts = full_data.split(":", 1)
    
    ip = parts[0].split("/", 2)[1]
    port = parts[0].split("/", 2)[2]
    
    self.add_device((ip, int(port)))
    
    if not self.received(parts[0]):
      self.rx.put(parts[1])
      self.register_received(parts[0])
      self.tx.put(full_data) # Gossip protocol