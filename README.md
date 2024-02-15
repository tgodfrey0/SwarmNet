# SwarmNet

A robust communications library for robot swarms. This is based on gossip protocols where the message will propagate around the swarm. When an agent receives a message it has not seen before, it will broadcast it to all other members of the swarm. 

This package is now [available on PyPi](https://pypi.org/project/swarmnet/)

## Usage

A `SwarmNet` object must be created that handles all of the communication. Only one instance should be created. To start the communication framework, the `start()` method must be run.

**All devices must use the same port number**

This `start()` command will broadcast a JOIN command to register with the rest of the swarm. 

## Message Parsers

Parsers are defined to handle incoming messages of specific types, for example, you may want to send `COUNT 1` to increase a distributed counter by 1 when the `COUNT` command is received. This would be defined as follows.

```python

counter = 0

def count_recv(msg: Optional[str]) -> None:
  counter += int(msg)

sn = SwarmNet({"COUNT": count_recv})
sn.start()

while(True):
  pass

sn.kill()

```

*It is important to remember that the parser functions are called from a different thread. Special care should be taken to ensure data integrity and consistency across threads.*

The type of each parser is `Optional[str] -> None` where the string is a string of any fields in the message. For example, if the message is `CMD field1 field2`, the string will be `"field1 field2`.

If a message is received with a command token for which there is no parser, an error message is produced with a list of recognised command tokens. To prevent error spam in more complex systems, you can set certain commands to be ignored by defining the parser as `None`. For example, if the above code was deployed in a swarm that also had `DEBUG` messages that were only important to one specific node, you could ignore them using `None`.

```python

counter = 0

def count_recv(msg: Optional[str]) -> None:
  counter += int(msg)

sn = SwarmNet({"COUNT": count_recv, "DEBUG": None})
sn.start()

while(True):
  pass

sn.kill()

```

## Message Format

All messages follow the format: `<CMD> <DATA1> <DATA2> ...`

A dictionary that maps command tokens to functions is passed to the `SwarmNet` constructor. The signature of this map is `Dict[str, Optional[Callable[[Optional[str]], None]]]` where the `str` passed to the parser function is the rest of the message string (if any)

Internally, every message is prefixed with an identifier that is not overwritten when the message is forwarded by receivers. This means agents will not parse their own message or parse the same message more than once.

