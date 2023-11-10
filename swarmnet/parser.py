import threading
import queue
from typing import Optional, Callable

import swarmnet.logger as logger
import swarmnet.discovery as discovery
import swarmnet.controller as controller

log = logger.Logger("parser")

class Parser:
  def __init__(self, mapping: {str: Callable[[Optional[str]], None]}, q: queue.Queue):
    self.fn_map = mapping
    self.msg_queue = q
    log.success("SwarmNet receiver thread successfully created")
  
  def parse_msg(self) -> None:
    msg: str = self.msg_queue.get(block=True).split(' ', 1)
    cmd: str = msg[0]
    data: Optional[str] = None
    
    if len(msg) > 1:
      data = msg[1]
      
    try:
      # self.ctrl.fn_map[cmd](data)
      threading.Thread(target=self.fn_map[cmd], args=[data]).start()
      log.info(f"Parse thread spawned to parse {cmd} command")
      
    except KeyError:
      log.error(f"No registered parser for command {cmd}")