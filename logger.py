from enum import Enum
import datetime

class Logger:
  class Colour_Code(Enum):
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    RED       = '\033[91m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    BLUE      = '\033[94m'
    PURPLE    = '\033[95m'
    CYAN      = '\033[96m'
      
  class Log_Level(Enum):
    INFO     = 0
    SUCCESS  = 1
    WARN     = 2
    ERROR    = 3
    CRITICAL = 4
    
  log_level = Log_Level.INFO

  def __init__(self, name):
    self.name = name
      
  def _log_normal(self, s: str, c: Colour_Code) -> None:
    print(f"{c.value}[{self.name}: {datetime.datetime.now()}] {s}{self.Colour_Code.ENDC.value}")
    
  def _log_bold(self, s: str, c: Colour_Code) -> None:
    print(f"{self.Colour_Code.BOLD.value}{c.value}[{self.name}: {datetime.datetime.now()}] {s}{self.Colour_Code.ENDC.value}")
    
  def _log_underlined(self, s: str, c: Colour_Code) -> None:
    print(f"{self.Colour_Code.UNDERLINE.value}{c.value}[{self.name}: {datetime.datetime.now()}] {s}{self.Colour_Code.ENDC.value}")
    
  def _log_bold_underlined(self, s: str, c: Colour_Code) -> None:
    print(f"{self.Colour_Code.BOLD.value}{self.Colour_Code.UNDERLINE.value}{c.value}[{self.name}: {datetime.datetime.now()}] {s}{self.Colour_Code.ENDC.value}")
    
  def info(self, s: str) -> None:
    if(self.log_level.value <= self.Log_Level.INFO.value):
      self._log_normal(s, self.Colour_Code.BLUE)
    
  def info_header(self, s: str) -> None:
    if(self.log_level.value <= self.Log_Level.INFO.value):
      self._log_bold(s, self.Colour_Code.CYAN)
    
  def success(self, s: str) -> None:
    if(self.log_level.value <= self.Log_Level.SUCCESS.value):
      self._log_bold_underlined(s, self.Colour_Code.GREEN)
    
  def warn(self, s: str) -> None:
    if(self.log_level.value <= self.Log_Level.WARN.value):
      self._log_bold(s, self.Colour_Code.YELLOW)
    
  def error(self, s: str) -> None:
    if(self.log_level.value <= self.Log_Level.ERROR.value):
      self._log_bold(s, self.Colour_Code.RED)
    
  def critical(self, s: str) -> None:
    if(self.log_level.value <= self.Log_Level.CRITICAL.value):
      self._log_bold_underlined(s, self.Colour_Code.RED)
      
      
def set_log_level(l: Logger.Log_Level):
  Logger.log_level = l