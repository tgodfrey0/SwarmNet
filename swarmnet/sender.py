import socket
import queue
from typing import List

import swarmnet.logger as logger

log = logger.Logger("sender")

class Sender:
  def __init__(self, port: int, tx_queue: queue.Queue):
    self.tx = tx_queue
    self.port = port
    log.success("SwarmNet sender started")
    
  def flush_queue(self, devices: List[str]):
    print("here")
    while(not self.tx.empty()):
      msg = self.tx.get()
      log.critical(f"Sending message: {msg}")
      for a in devices:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((a, self.port))
        soc.send(msg)
        soc.close()
