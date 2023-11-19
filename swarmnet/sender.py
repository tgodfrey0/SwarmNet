import socket
import queue
from typing import List

import swarmnet.logger as logger

log = logger.Logger("sender")

class Sender:
  def __init__(self, self_addr: str, port: int, tx_queue: queue.Queue):
    self.tx = tx_queue
    self.port = port
    self.self_addr = self_addr
    log.success("SwarmNet sender started")
    
  def flush_queue(self):
    while(not self.tx.empty()):
      msg = self.tx.get()
      log.info(f"Sending message: {msg}")
      for addr in range(2,255):
        if(str(addr) == self.self_addr.split(".")[3]):
          continue
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(addr)
        sock.settimeout(10)
        # soc.connect((f"192.168.0.{addr}", self.port))
        # soc.send(msg)
        sock.sendto(bytes(msg + "\n", "utf-8"), (f"192.168.0.{addr}", self.port))
        sock.close()
      log.success("Message sent to all devices on the network")
