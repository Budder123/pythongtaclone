from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from src.world import World
from src.player import Player

class Game(ShowBase):
    def __init__(self):
        super().__init__()

        # Set background color and disable mouse
        self.win.setClearColor((0.4, 0.7, 1.0, 1.0))
        self.disableMouse()

        # Initialize world and player
        self.world = World(self)
        self.player = Player(self)

        # Set up camera
        self.camera.setPos(0, 0, 50)
        self.camera.setP(-90)

        # Set up collision detection
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # Add the player's collider to the handler and the traverser
        self.pusher.addCollider(self.player.collider_node, self.player.node)
        self.cTrav.addCollider(self.player.collider_node, self.pusher)

        # Uncomment this line to see the collision solids
        # self.cTrav.showCollisions(self.render)

        # Game loop
        self.taskMgr.add(self.gameLoop, "gameLoop")

    def gameLoop(self, task):
        """The main game loop, which updates game state and camera."""
        dt = globalClock.getDt()

        # Update the player's movement
        self.player.update(dt)

        # Run the collision traversal
        self.cTrav.traverse(self.render)

        # Update the camera to follow the player
        self.camera.setPos(self.player.node.getX(), self.player.node.getY(), 50)

        return task.cont

# Create an instance of the game and run it
app = Game()
app.run()
