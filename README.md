# SwarmNet

A robust communications library for robot swarms. This is based on gossip protocols where the message will propagate around the swarm. When an agent receives a message it has not seen before, it will broadcast it to all other members of the swarm. 

## Usage

A `SwarmNet` object must be created that handles all of the communication. Only one instance should be created. To start the communication framework, the `start()` method must be run.

**All devices must use the same port number**

This `start()` command will broadcast a JOIN command to register with the rest of the swarm. 

## Message Format

All messages follow the format: `<CMD> <DATA1> <DATA2> ...`

A dictionary that maps command tokens to functions is passed to the `SwarmNet` constructor. The signature of this map is `Dict[str, Callable[[Optional[str]], None]]` where the `str` passed to the parser function is the rest of the message string (if any)

Internally, every message is prefixed with an identifier that is not overwritten when the message is forwarded by receivers. This means agents will not parse their own message or parse the same message more than once.

