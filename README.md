# SwarmNet
A Bluetooth-based, robust communications library for robot swarms.

## Message Format

All messages follow the format: `<CMD> <DATA1> <DATA2> ...`. A dictionary that maps command tokens to functions is passed to the `SwarmNet` constructor. The signature of this map is `{str: Callable[[Optional[str]], None]}` where the `str` passed to the parser function is the rest of the message string (if any)