import swarmnet
from typing import Optional
from threading import Lock

can_cont: bool = False
lock: Lock = Lock()

def get_cont():
  lock.acquire()
  b = can_cont
  lock.release()
  return b

def set_cont(b):
  global can_cont
  lock.acquire()
  can_cont = b
  lock.release()

def ready_recv(msg: Optional[str]) -> None:
  set_cont(True)
  print("Ready to continue")

def text_recv(msg: Optional[str]) -> None:
  print(f"Message received: {msg}")

if __name__=="__main__":
  ctrl = swarmnet.SwarmNet({"TEXT": text_recv, "READY": ready_recv}, device_list=[("192.168.0.120", 51000), ("192.168.0.121", 51000)])
  ctrl.start()
  
  while(get_cont()):
    ctrl.send("READY")
  
  ctrl.send("TEXT hello world")