from swarmnet import SwarmNet
import typing

def out(s: typing.Optional[str]) -> None:
  print(s)

if __name__=="__main__":
  controller = SwarmNet({"TEXT": out})
  controller.start()
  input("Press any key to send a message")
  controller.send("TEXT hello world!")
  input("Press any key to kill all threads")
  controller.kill()
  