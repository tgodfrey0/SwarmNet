from swarmnet.controller import SwarmNet


if __name__=="__main__":
  controller = SwarmNet("swarm-", {})
  controller.start()
  input("")
  print("A")
  controller.send("TEXT hello world!")
  print("B")
  input("")
  controller.kill()
  