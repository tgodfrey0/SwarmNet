from swarmnet.controller import SwarmNet
import typing

def out(s: typing.Optional[str]) -> None:
  print(s)

if __name__=="__main__":
  controller = SwarmNet({"TEXT": out})
  controller.start()
  input("")
  print("A")
  controller.send("TEXT hello world!")
  print("B")
  input("")
  controller.kill()
  