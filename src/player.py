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

        model = self.base.loader.loadModel("models/box")
        model.reparentTo(self.node)
        model.setScale(0.5, 1, 0.5) # Make it look more like a car
        self.node.setColor(1, 0, 0, 1)

        # Keyboard input state
        self.keyMap = {
            "forward": False, "backward": False, "left": False, "right": False
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
        # Apply rotation
        if self.keyMap["left"]:
            self.node.setH(self.node.getH() + 150 * dt)
        if self.keyMap["right"]:
            self.node.setH(self.node.getH() - 150 * dt)

        # Apply movement (relative to the player's current rotation)
        if self.keyMap["forward"]:
            self.node.setY(self.node, 20 * dt)
        if self.keyMap["backward"]:
            self.node.setY(self.node, -10 * dt)
