from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, GraphicsOutput, GraphicsPipe, FrameBufferProperties, WindowProperties, OrthographicLens, AmbientLight, DirectionalLight
from src.world import World
from src.player import Player
from src.ui import UI

class Game(ShowBase):
    def __init__(self):
        super().__init__()

        # Set background color and disable mouse
        self.win.setClearColor((0.4, 0.7, 1.0, 1.0))
        self.disableMouse()

        # Enable the automatic shader generator for lighting and shadows
        self.render.setShaderAuto()

        # --- Lighting Setup ---
        # Add an ambient light to softly illuminate the whole scene
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.3, 0.3, 0.3, 1))
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)

        # Add a directional light to simulate the sun
        dir_light = DirectionalLight('dir_light')
        dir_light.setColor((0.8, 0.8, 0.7, 1))
        dir_light_np = self.render.attachNewNode(dir_light)
        dir_light_np.setHpr(0, -60, 0)  # Angle the light down
        self.render.setLight(dir_light_np)

        # Enable shadows for the directional light
        dir_light.setShadowCaster(True, 2048, 2048)
        dir_light.getLens().setFilmSize(200, 200) # Set the area covered by shadows
        dir_light.getLens().setNearFar(10, 200)

        # Initialize world and player
        self.world = World(self)
        self.player = Player(self)

        # Set up main camera
        self.camera.setPos(0, 0, 50)
        self.camera.setP(-90)

        # Set up the minimap
        self.minimap_buffer = self.win.makeTextureBuffer("Minimap", 256, 256)
        self.minimap_cam = self.makeCamera(self.minimap_buffer)
        self.minimap_cam.reparentTo(self.render)
        self.minimap_cam.setPos(self.player.node.getX(), self.player.node.getY(), 150)
        self.minimap_cam.setP(-90)

        # Use an orthographic lens for the minimap for a true 2D look
        lens = OrthographicLens()
        lens.setFilmSize(100, 100)  # The area covered by the minimap camera
        self.minimap_cam.node().setLens(lens)

        # Initialize UI last, passing the minimap texture to it
        self.ui = UI(self, self.player, self.minimap_buffer.getTexture())

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

        # Update the UI
        self.ui.update()

        # Run the collision traversal
        self.cTrav.traverse(self.render)

        # Update the cameras to follow the player
        self.camera.setPos(self.player.node.getX(), self.player.node.getY(), 50)
        self.minimap_cam.setPos(self.player.node.getX(), self.player.node.getY(), 150)

        return task.cont

# Create an instance of the game and run it
app = Game()
app.run()
