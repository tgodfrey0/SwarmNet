import queue
import bluetooth

import swarmnet.logger as logger

log = logger.Logger("receiver")

class Receiver:
  def __init__(self, addr: str, rx_queue: queue.Queue, tx_queue: queue.Queue):
    self.listener = bluetooth.BluetoothSocket()
    self.listener.bind((addr, bluetooth.PORT_ANY))
    self.listener.listen(1)
    self.port = self.listener.getsockname()[1]
    self.rx = rx_queue
    self.tx = tx_queue

    log.info(f"Waiting for connection on RFCOMM channel {self.port}")
    log.success("SwarmNet receiver started")
    
  def accept_connection(self) -> None:
    client_sock, client_info = self.listener.accept()
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
    
    self.rx.put(full_data)
    self.tx.put(full_data) # Gossip protocol