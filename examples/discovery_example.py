from swarmnet.controller import SwarmNet


if __name__=="__main__":
  controller = SwarmNet("swarm-", {}, "3C:9C:0F:FB:12:50")
  controller.start()
  input("")
  controller.kill()
  