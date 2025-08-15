from direct.gui.DirectGui import OnscreenText, DirectWaitBar, OnscreenImage
from panda3d.core import TextNode, TransparencyAttrib

class UI:
    def __init__(self, base, player, minimap_texture):
        """
        Initializes the User Interface.

        :param base: The ShowBase instance.
        :param player: The player instance to get data from.
        :param minimap_texture: The texture for the minimap.
        """
        self.base = base
        self.player = player

        # MPH Gauge
        self.mph_text = OnscreenText(
            text="MPH: 0",
            pos=(-1.3, 0.9),  # Top-left corner
            scale=0.07,
            fg=(1, 1, 1, 1),  # White
            shadow=(0, 0, 0, 0.5),
            align=TextNode.ALeft
        )

        # Wanted Level
        self.wanted_text = OnscreenText(
            text="", # Initially empty
            pos=(1.3, 0.9),  # Top-right corner
            scale=0.1,
            fg=(1, 0.9, 0.1, 1),  # Gold
            shadow=(0, 0, 0, 0.5),
            align=TextNode.ARight
        )

        # Boost Bar
        self.boost_bar = DirectWaitBar(
            text="",
            value=100,
            pos=(-1.3, 0, 0.8), # Below the MPH gauge
            scale=(0.2, 1, 0.5),
            barColor=(0.1, 0.6, 1.0, 1), # Blue
            frameSize=(-0.25, 0.25, -0.05, 0.05)
        )

        # Minimap
        # The OnscreenImage class will display our minimap texture
        self.minimap_image = OnscreenImage(
            image=minimap_texture,
            pos=(1.1, 0, -0.75), # Bottom-right corner
            scale=(0.25, 1, 0.25)
        )
        # Make the minimap circular by applying a mask
        self.minimap_image.setTransparency(TransparencyAttrib.MAlpha)

    def update(self):
        """
        Updates the UI elements every frame.
        """
        # Update MPH
        self.mph_text.setText(f"MPH: {self.player.speed:.0f}")

        # Update Wanted Level with star characters
        self.wanted_text.setText("★" * self.player.wanted_level)

        # Update Boost Bar
        self.boost_bar['value'] = self.player.boost_level
