from panda3d.core import LVector3, CollisionNode, CollisionSphere, BitMask32

class Player:
    def __init__(self, base):
        """
        Initializes the player, including model, controls, and collision setup.

        :param base: The ShowBase instance.
        """
        self.base = base

        # Create the player node and attach the model to it
        self.node = self.base.render.attachNewNode("player")
        self.node.setPos(0, 0, 0.5)

        # Create a more detailed car model from basic shapes
        chassis = self.base.loader.loadModel("models/box")
        chassis.reparentTo(self.node)
        chassis.setScale(0.7, 1.2, 0.3)  # Wider, longer, flatter
        chassis.setPos(0, 0, 0)
        chassis.setColor(0.8, 0.1, 0.1, 1)  # Dark red

        cabin = self.base.loader.loadModel("models/box")
        cabin.reparentTo(self.node)
        cabin.setScale(0.5, 0.6, 0.3)  # Smaller cabin on top
        cabin.setPos(0, -0.1, 0.3)  # Positioned towards the back of the chassis
        cabin.setColor(0.6, 0.1, 0.1, 1)  # A slightly different shade of red

        # Add headlights
        headlight_l = self.base.loader.loadModel("models/box")
        headlight_l.reparentTo(self.node)
        headlight_l.setScale(0.1, 0.05, 0.1)
        headlight_l.setPos(-0.5, 1.2, 0.1) # The chassis is 1.2 units long in Y
        headlight_l.setColor(1, 1, 0.5, 1)

        headlight_r = self.base.loader.loadModel("models/box")
        headlight_r.reparentTo(self.node)
        headlight_r.setScale(0.1, 0.05, 0.1)
        headlight_r.setPos(0.5, 1.2, 0.1)
        headlight_r.setColor(1, 1, 0.5, 1)

        # Add taillights
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

        # Game state variables
        self.speed = 0.0
        self.wanted_level = 0
        self.boost_level = 100.0

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
        c_solid = CollisionSphere(0, 0, 0.5, 1.2) # Center and radius
        self.collider_node = self.node.attachNewNode(CollisionNode('player_collider'))
        self.collider_node.node().addSolid(c_solid)

        # Set this as a dynamic, "into" object that collides into other things
        self.collider_node.node().setFromCollideMask(BitMask32.allOff())
        self.collider_node.node().setIntoCollideMask(BitMask32.bit(1))

    def updateKeyMap(self, key, value):
        """Callback to update the keymap."""
        self.keyMap[key] = value

    def update(self, dt):
        """
        Updates the player's state each frame.
        """
        # --- Boost Logic ---
        is_boosting = self.keyMap["boost"] and self.boost_level > 0

        if is_boosting:
            # Drain boost level while boosting
            self.boost_level = max(0, self.boost_level - 25 * dt)
        else:
            # Regenerate boost level when not boosting
            self.boost_level = min(100, self.boost_level + 10 * dt)

        # --- Speed and Movement Logic ---
        forward_speed = 40 if is_boosting else 20
        backward_speed = 10
        mph_conversion_factor = 3.5

        if self.keyMap["forward"]:
            self.speed = forward_speed * mph_conversion_factor
            self.node.setY(self.node, forward_speed * dt)
        elif self.keyMap["backward"]:
            self.speed = backward_speed * mph_conversion_factor
            self.node.setY(self.node, -backward_speed * dt)
        else:
            self.speed = 0

        # --- Rotation Logic ---
        if self.keyMap["left"]:
            self.node.setH(self.node.getH() + 150 * dt)
        if self.keyMap["right"]:
            self.node.setH(self.node.getH() - 150 * dt)
