import bluetooth
import queue
from typing import Dict

import swarmnet.logger as logger

log = logger.Logger("sender")

class Sender:
  def __init__(self, tx_queue: queue.Queue):
    self.tx = tx_queue
    log.success("SwarmNet sender started")
    
  def flush_queue(self, devices: Dict[str, str]):
    print("here")
    while(not self.tx.empty()):
      log.info("Sending message")
      msg = self.tx.get()
      for n,a in devices.items():
        soc = bluetooth.BluetoothSocket()
        soc.bind((a, bluetooth.PORT_ANY))
        soc.send(msg)
        soc.close()
