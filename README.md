# Components, top to bottom

1. Scripts, which run sequences of animations
1. The parkertree module, which contains the client/server code, the animation primitives, and a simulator using pygame.
1. The Arduino/RP2350 firmware

# Comms

Client() and Server() in parkertree.remote use ZeroMQ over TCP to transmit a few message types, implemented as classes.

The link between the server and the LED driver module is SPI, with a few defined commands.  The first byte is a command ID, with the rest of the packet is unique per command.

CMDClear - Set all LEDs to black.
| 0x68 |

CMDShow - Tell the LED driver to display the current frame.
| 0x1e |

CMDSingle - Directly set the color of one LED by index.
| 0x10 | 16-bit LED ID | 8-bit red | 8-bit green | 8-bit blue |

CMDString - Set lots of LEDs at once.
| 0x14 | 16-bit LED ID | 8-bit red | 8-bit green | 8-bit blue |... up to 64 copies of ID-R-G-B.
