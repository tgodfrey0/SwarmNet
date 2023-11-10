import threading
from typing import Optional

import swarmnet.logger as log
import swarmnet.discovery as dis

logger = log.Logger("Controller")

class SwarmNet(threading.Thread):
  def __init__(self, pref: str, bt_device_retries: int = 3):
    self.swarm_prefix = pref
    self.discovery_retries = bt_device_retries
    
    logger.success("SwarmNet controller successfully created")
  
  def start_communication_framework(self):
    i = 0
    for i in range(0, self.discovery_retries):
      ds = dis.discover_swarm_devices(self.swarm_prefix)
      if ds != {}:
        self.swarm_list = ds
        break;
      logger.info("Retrying swarm discovery")
    
    if i == (self.discovery_retries-1):
      logger.error(f"Retry limit ({self.discovery_retries}) reached during swarm discovery")
  
  def set_log_level(lv: log.Logger.Log_Level):
    logger.set_log_level(lv)