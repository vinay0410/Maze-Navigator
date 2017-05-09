# Terrain Navigator

A bot driven by Raspberry Pi which navigates a circular maze, by visiting all checkpoints to the center of the maze. Also the bot is guided by the base station via a laser pointer which, is driven by NodeMCU(ESP8266).

A sample maze looks something like this:
![Maze](images/MAP.jpg= 200x200 "Maze")


So, First the Computer processes this image to calulate the shortest Optimum path from Start to the Centre.

Then This path is sent to NodeMCU(ESP8266) which then guides a Raspberry Pi driven Bot using a Laser pointer.

Both the systems are also in communication with each at every point through WiFi to notify each other of the current situation, which may include acknowledging a checkpoint, whether the laser is visible to the rover or not, search protocol to be followed if the rover is lost, etc.
