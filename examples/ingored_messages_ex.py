import swarmnet
from typing import Optional
from threading import Lock
from time import sleep

if __name__=="__main__":
  ctrl = swarmnet.SwarmNet({"TEXT": print, "INFO": None}, device_list=[("192.168.0.120", 51000), ("192.168.0.121", 51000)])
  ctrl.start()
  ctrl.rx_queue.put("READY") # Should produce an error
  
  sleep(1)
  
  ctrl.rx_queue.put("INFO") # Should not produce any output
  
  sleep(1)
  
  ctrl.rx_queue.put("TEXT Hello World!") # Should print "Hello World!"
  
  sleep(1)
  
  ctrl.kill()