import threading

import swarmnet.logger as logger
import swarmnet.discovery as discovery
import swarmnet.controller as controller

log = logger.Logger("receiver")

class Receiver:
  def __init__(self, ctrl: controller.SwarmNet):
    self.ctrl = ctrl
    log.info("SwarmNet receiver thread successfully created")