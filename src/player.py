from panda3d.core import LVector3, CollisionNode, CollisionSphere, BitMask32, CardMaker, Texture, PNMImage, NodePath
from direct.interval.IntervalGlobal import Sequence, LerpColorScaleInterval, Func
from src.vfx import create_boost_effect

class Player:
    def __init__(self, base, sound_manager):
        """
        Initializes the player, including model, controls, and physics.

        :param base: The ShowBase instance.
        :param sound_manager: The game's sound manager.
        """
        self.base = base
        self.sound_manager = sound_manager

        # Create the player node and attach the model to it
        self.node = self.base.render.attachNewNode("player")
        self.node.setPos(0, 0, 0.5)

        # Create a more detailed car model from basic shapes
        chassis = self.base.loader.loadModel("models/box")
        chassis.reparentTo(self.node)
        chassis.setScale(0.7, 1.2, 0.3)
        chassis.setPos(0, 0, 0)
        chassis.setColor(0.8, 0.1, 0.1, 1)

        cabin = self.base.loader.loadModel("models/box")
        cabin.reparentTo(self.node)
        cabin.setScale(0.5, 0.6, 0.3)
        cabin.setPos(0, -0.1, 0.3)
        cabin.setColor(0.6, 0.1, 0.1, 1)

        # Add headlights and taillights
        headlight_l = self.base.loader.loadModel("models/box")
        headlight_l.reparentTo(self.node)
        headlight_l.setScale(0.1, 0.05, 0.1)
        headlight_l.setPos(-0.5, 1.2, 0.1)
        headlight_l.setColor(1, 1, 0.5, 1)
        headlight_r = self.base.loader.loadModel("models/box")
        headlight_r.reparentTo(self.node)
        headlight_r.setScale(0.1, 0.05, 0.1)
        headlight_r.setPos(0.5, 1.2, 0.1)
        headlight_r.setColor(1, 1, 0.5, 1)
        taillight_l = self.base.loader.loadModel("models/box")
        taillight_l.reparentTo(self.node)
        taillight_l.setScale(0.1, 0.05, 0.1)
        taillight_l.setPos(-0.5, -1.2, 0.1)
        taillight_l.setColor(1, 0, 0, 1)
        taillight_r = self.base.loader.loadModel("models/box")
        taillight_r.reparentTo(self.node)
        taillight_r.setScale(0.1, 0.05, 0.1)
        taillight_r.setPos(0.5, -1.2, 0.1)
        taillight_r.setColor(1, 0, 0, 1)

        # VFX
        self.boost_vfx = create_boost_effect(self.base)
        self.boost_vfx.reparentTo(self.node)
        self.boost_vfx.setPos(0, -1.3, 0.2) # Position at the back of the car
        self.skid_texture = self._create_skid_texture()
        self.skid_timer = 0.0
        self.skid_interval = 0.05 # Time between skid marks
        self.skid_card_maker = CardMaker('skidmark_cm')
        self.skid_card_maker.setFrame(-0.5, 0.5, -1.5, 1.5)

        # Physics and State Variables
        self.current_speed = 0.0
        self.acceleration = 20.0
        self.deceleration = 30.0
        self.max_speed = 40.0
        self.max_boost_speed = 70.0
        self.steering_speed = 120.0
        self.top_speed = self.max_boost_speed * 3.5 # For UI and sound pitch
        self.wanted_level = 0
        self.boost_level = 100.0
        self.was_boosting = False

        # Keyboard input state
        self.keyMap = {
            "forward": False, "backward": False, "left": False, "right": False, "boost": False
        }

        # Register key events
        self.base.accept("w", self.updateKeyMap, ["forward", True])
        self.base.accept("w-up", self.updateKeyMap, ["forward", False])
        self.base.accept("s", self.updateKeyMap, ["backward", True])
        self.base.accept("s-up", self.updateKeyMap, ["backward", False])
        self.base.accept("a", self.updateKeyMap, ["left", True])
        self.base.accept("a-up", self.updateKeyMap, ["left", False])
        self.base.accept("d", self.updateKeyMap, ["right", True])
        self.base.accept("d-up", self.updateKeyMap, ["right", False])
        self.base.accept("shift", self.updateKeyMap, ["boost", True])
        self.base.accept("shift-up", self.updateKeyMap, ["boost", False])

        # Set up player collision
        c_solid = CollisionSphere(0, 0, 0.5, 1.2)
        self.collider_node = self.node.attachNewNode(CollisionNode('player_collider'))
        self.collider_node.node().addSolid(c_solid)
        self.collider_node.node().setFromCollideMask(BitMask32.allOff())
        self.collider_node.node().setIntoCollideMask(BitMask32.bit(1))

    def _create_skid_texture(self):
        """Generates a simple, semi-transparent black texture for skid marks."""
        img = PNMImage(64, 128, 4)
        img.addAlpha()
        img.fill(0, 0, 0)
        img.alpha_fill(0)
        # renderSpot takes (fg, bg, radius, falloff). It renders in the center.
        img.renderSpot(
            (1, 1, 1, 0.4), # Faint white color with alpha
            (0.5, 0.5, 0.5, 0.0), # Fade to transparent
            60, 30 # Radius, falloff
        )
        tex = Texture()
        tex.load(img)
        return tex

    def updateKeyMap(self, key, value):
        """Callback to update the keymap."""
        self.keyMap[key] = value

    def update(self, dt):
        """Updates the player's physics and state each frame."""
        # --- Get input and state ---
        is_accelerating = self.keyMap["forward"]
        is_braking = self.keyMap["backward"]
        is_turning = self.keyMap["left"] or self.keyMap["right"]
        is_boosting = self.keyMap["boost"] and self.boost_level > 0

        # --- Boost sound and VFX logic ---
        if is_boosting and not self.was_boosting:
            self.sound_manager.play_boost()
            self.boost_vfx.start()
        elif not is_boosting and self.was_boosting:
            self.boost_vfx.softStop()

        self.was_boosting = is_boosting

        if is_boosting:
            self.boost_level = max(0, self.boost_level - 20 * dt)
        else:
            self.boost_level = min(100, self.boost_level + 15 * dt)

        # --- Acceleration and Speed ---
        target_max_speed = self.max_boost_speed if is_boosting else self.max_speed

        if is_accelerating:
            self.current_speed += self.acceleration * dt
        elif is_braking:
            self.current_speed -= self.deceleration * 1.5 * dt
        else:
            # Natural friction
            if self.current_speed > 0:
                self.current_speed -= self.deceleration * dt
            elif self.current_speed < 0:
                self.current_speed += self.deceleration * dt

        # Clamp speed
        if abs(self.current_speed) < 0.5: self.current_speed = 0
        self.current_speed = max(-self.max_speed * 0.5, min(target_max_speed, self.current_speed))

        # --- Drifting and Steering ---
        is_drifting = is_turning and abs(self.current_speed) > self.max_speed * 0.4
        self.sound_manager.toggle_skid(is_drifting)

        if is_drifting:
            self.skid_timer += dt
            if self.skid_timer > self.skid_interval:
                self.skid_timer = 0
                self._create_skid_mark()

        steering = self.steering_speed
        if is_drifting:
            steering *= 1.25 # More responsive steering while drifting

        # Steering is less effective at very high speeds
        steering_factor = 1.0 - (abs(self.current_speed) / (target_max_speed * 2.0))
        steering *= steering_factor

        if self.keyMap["left"]:
            self.node.setH(self.node.getH() + steering * dt)
        if self.keyMap["right"]:
            self.node.setH(self.node.getH() - steering * dt)

        # --- Apply final movement ---
        self.node.setY(self.node, self.current_speed * dt)

        # --- Update speed for UI ---
        self.speed = abs(self.current_speed * 3.5) # Arbitrary conversion to MPH

    def _create_skid_mark(self):
        """Creates a skid mark quad under the car's rear wheels."""
        # Create a NodePath for each wheel's skid
        for side in [-1, 1]: # Left and right wheels
            skid_np = NodePath(self.skid_card_maker.generate())
            skid_np.setTexture(self.skid_texture)
            skid_np.setTransparency(True)

            # Position relative to the car, then reparent to render
            # to leave it behind on the world
            skid_np.reparentTo(self.base.render)
            skid_np.setPos(self.node, 0.5 * side, -0.8, 0.01)
            skid_np.setHpr(self.node.getHpr())
            skid_np.setR(-90) # Rotate card to be flat

            # Fade out and destroy the skid mark
            fade_out = LerpColorScaleInterval(skid_np, 1.5, (1,1,1,0), (1,1,1,0.5))
            destroy = Func(skid_np.destroy)
            Sequence(fade_out, destroy).start()
