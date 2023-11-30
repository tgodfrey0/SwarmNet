from swarmnet import SwarmNet


if __name__=="__main__":
  controller = SwarmNet({})
  controller.start()
  input("")
  print("A")
  controller.send("TEXT hello world!")
  print("B")
  input("")
  controller.kill()
  