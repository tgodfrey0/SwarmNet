import queue
import socket
from typing import Callable
import swarmnet.logger as logger

log = logger.Logger("receiver")

class Receiver:
  def __init__(self, received: Callable[[str], bool], register_received: Callable[[str], None], port: int, rx_queue: queue.Queue, tx_queue: queue.Queue):
    self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.listener.bind(('localhost', port))
    self.listener.listen()
    self.received = received
    self.register_received = register_received
    self.rx = rx_queue
    self.tx = tx_queue

    log.info("Waiting for connections")
    log.success("SwarmNet receiver started")
    
  def accept_connection(self) -> None:
    print("IN FUNC")
    client_sock, client_info = self.listener.accept() # This waits indefinitely 
    logger.info(f"Connection received")

    full_data = ""
    try:
      while True:
        data = client_sock.recv(1024)
        if not data:
          break
        full_data += data
    except OSError:
      pass
    
    parts = full_data.split(":", 1)
    if not self.received(parts[0]):
      self.rx.put(parts[1])
      self.register_received(parts[0])
      self.tx.put(full_data) # Gossip protocol