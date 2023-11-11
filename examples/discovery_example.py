from swarmnet.controller import SwarmNet


if __name__=="__main__":
  controller = SwarmNet("swarm-", {}, 2)
  controller.start()
  input("a: ")
  controller.kill()
  