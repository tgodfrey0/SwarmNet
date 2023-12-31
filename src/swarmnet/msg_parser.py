import threading
import queue
from typing import Optional, Callable, Dict

from . import logger

log = logger.Logger("parser")

class MessageParser:
  def __init__(self, mapping: Dict[str, Callable[[Optional[str]], None]], q: queue.Queue):
    self.fn_map = mapping
    self.msg_queue = q
    log.success("SwarmNet parser started")
  
  def parse_msg(self) -> None:
    msg: str = self.msg_queue.get(block=True).split(' ', 1)
    cmd: str = msg[0].strip()
    data: Optional[str] = None
    
    if len(msg) > 1:
      data = msg[1]
      
    try:
      f = self.fn_map[cmd]
      if(f is not None):
        threading.Thread(target=f, args=[data]).start()
        log.info(f"Parse thread spawned to parse {cmd} command")
      
    except KeyError:
      log.error(f"No registered parser for command {cmd}")
      log.error("Registered parsers exist for commands:")
      for c in self.fn_map.keys():
        if(c == "JOIN"):
          continue
        
        if(self.fn_map[c] is None):
          log.error(f"{c} (Ignored)")
        else:
          log.error(c)