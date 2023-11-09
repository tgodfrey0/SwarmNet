import threading

import logger
import discovery

logger = logger.Logger("Controller")

class SwarmNet(threading.Thread):
  def __init__(self):
    pass
  
  def start_communication_framework():
    pass
  
  def set_log_level(l: logger.Logger.Log_Level):
    logger.set_log_level(l)