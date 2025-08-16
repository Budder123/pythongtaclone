from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionHandlerEvent, GraphicsOutput, GraphicsPipe, FrameBufferProperties, WindowProperties, OrthographicLens, AmbientLight, DirectionalLight, LVector3, Vec3
from direct.interval.IntervalGlobal import Sequence, Wait, Func
import random
from src.world import World
from src.player import Player
from src.ui import UI
from src.sound import SoundManager
from src.vfx import create_sparks_effect

class Game(ShowBase):
    def __init__(self):
        super().__init__()

        self.win.setClearColor((0.4, 0.7, 1.0, 1.0))
        self.disableMouse()
        # self.render.setShaderAuto()

        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor((0.3, 0.3, 0.3, 1))
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)

        dir_light = DirectionalLight('dir_light')
        dir_light.setColor((0.8, 0.8, 0.7, 1))
        dir_light_np = self.render.attachNewNode(dir_light)
        dir_light_np.setHpr(0, -60, 0)
        self.render.setLight(dir_light_np)

        dir_light.setShadowCaster(True, 2048, 2048)
        dir_light.getLens().setFilmSize(200, 200)
        dir_light.getLens().setNearFar(10, 200)

        self.world = World(self)
        self.sound_manager = SoundManager(self)
        spawn_point = self.world.get_safe_spawn_point()
        self.player = Player(self, self.sound_manager, spawn_point)

        # Set up the minimap camera (remains top-down)
        self.minimap_buffer = self.win.makeTextureBuffer("Minimap", 256, 256)
        self.minimap_cam = self.makeCamera(self.minimap_buffer)
        self.minimap_cam.reparentTo(self.render)
        self.minimap_cam.setPos(self.player.node.getX(), self.player.node.getY(), 150)
        self.minimap_cam.setP(-90)
        lens = OrthographicLens()
        lens.setFilmSize(100, 100)
        self.minimap_cam.node().setLens(lens)

        self.ui = UI(self, self.player, self.minimap_buffer.getTexture())

        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.event_handler = CollisionHandlerEvent()
        self.event_handler.addInPattern('%fn-collided')
        self.accept('player_collider-collided', self.handle_collision)
        self.pusher.addCollider(self.player.collider_node, self.player.node)
        self.cTrav.addCollider(self.player.collider_node, self.pusher)
        self.cTrav.addCollider(self.player.collider_node, self.event_handler)

        self.taskMgr.add(self.gameLoop, "gameLoop")
        self.sound_manager.start_engine()
        self.shake_duration = 0.0
        self.shake_magnitude = 0.8
        self.sparks_vfx = create_sparks_effect(self)


    def handle_collision(self, entry):
        if abs(self.player.current_speed) > 10:
            self.sound_manager.play_collision()
            self.shake_duration = 0.2
            collision_point = entry.getSurfacePoint(self.render)
            sparks = self.sparks_vfx.make_copy()
            sparks.setPos(collision_point)
            Sequence(Func(sparks.start), Wait(1.0), Func(sparks.cleanup)).start()

    def gameLoop(self, task):
        dt = globalClock.getDt()

        self.player.update(dt)
        self.ui.update()
        self.sound_manager.update(self.player.speed, self.player.top_speed)
        self.cTrav.traverse(self.render)

        # --- Camera Logic ---
        # 1. Calculate desired position (behind and above player)
        # Get the vector pointing behind the player in world space
        behind_vec = self.render.getRelativeVector(self.player.node, Vec3(0, -1, 0))
        behind_vec.normalize()
        desired_pos = self.player.node.getPos() + behind_vec * 15 + Vec3(0, 0, 6)

        # 2. Smoothly interpolate to the desired position
        lerp_speed = 10 * dt
        current_pos = self.camera.getPos()
        new_pos = current_pos + (desired_pos - current_pos) * lerp_speed
        self.camera.setPos(new_pos)

        # 3. Always look at the player
        self.camera.lookAt(self.player.node.getPos() + Vec3(0, 0, 1))

        # 4. Apply camera shake if active
        if self.shake_duration > 0:
            self.shake_duration -= dt
            self.camera.setX(self.camera, random.uniform(-self.shake_magnitude, self.shake_magnitude))
            self.camera.setY(self.camera, random.uniform(-self.shake_magnitude, self.shake_magnitude))

        # 5. Update minimap camera (still top-down)
        self.minimap_cam.setPos(self.player.node.getX(), self.player.node.getY(), 150)

        return task.cont

app = Game()
app.run()
