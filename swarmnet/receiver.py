import queue
import socketserver
from typing import Callable
import swarmnet.logger as logger
import threading

log = logger.Logger("receiver")

class Receiver:
  class Handler(socketserver.DatagramRequestHandler):
    def handle(self):
      msg = self.rfile.readline().strip().decode("utf-8")
      parts = msg.split(":", 1)
      if not self.received(parts[0]):
        super.rx.put(parts[1])
        super.register_received(parts[0])
        super.tx.put(msg) # Gossip protocol
      
  def __init__(self, addr: str, port: int, received: Callable[[str], bool], register_received: Callable[[str], None], rx_queue: queue.Queue, tx_queue: queue.Queue):
    # self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # self.listener.bind((addr, port))
    # self.listener.listen()
    # self.listener.settimeout(10)
    self.listener = socketserver.UDPServer((addr, port), self.Handler)
    self.received = received
    self.register_received = register_received
    self.rx = rx_queue
    self.tx = tx_queue
  
    threading.Thread(target=self.listener.serve_forever)
    log.info("Waiting for connections")
    log.success("SwarmNet receiver started")
    
  def control_receiver(self, exit_request: bool) -> None:
    if(exit_request):
      self.listener.shutdown()
    
  # def accept_connection(self) -> None:
  #   try:
  #     client_sock, client_info = self.listener.accept() # This waits indefinitely 
  #   except TimeoutError:
  #     return
    
  #   logger.info(f"Connection received")

  #   full_data = ""
  #   try:
  #     while True:
  #       data = client_sock.recv(1024)
  #       if not data:
  #         break
  #       full_data += data
  #   except OSError:
  #     pass
    
  #   parts = full_data.split(":", 1)
  #   if not self.received(parts[0]):
  #     self.rx.put(parts[1])
  #     self.register_received(parts[0])
  #     self.tx.put(full_data) # Gossip protocol