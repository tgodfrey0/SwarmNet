import threading

import swarmnet.logger as logger
import swarmnet.discovery as discovery
import swarmnet.controller as controller

log = logger.Logger("sender")

class Sender:
  def __init__(self, ctrl: controller.SwarmNet):
    self.ctrl = ctrl
    log.success("SwarmNet controller successfully created")
