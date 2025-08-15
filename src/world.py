from panda3d.core import CardMaker, CollisionNode, CollisionBox, Point3, BitMask32, PNMImage, Texture, TextureStage
import random

class World:
    def __init__(self, base):
        """
        Initializes the game world, including the ground plane and city.

        :param base: The ShowBase instance.
        """
        self.base = base
        self.buildings = []
        self.building_texture = self._create_building_texture()
        self.road_texture = self._create_road_texture()

        # Set up the ground plane
        cm = CardMaker('ground')
        cm.setFrame(-100, 100, -100, 100)
        self.ground = self.base.render.attachNewNode(cm.generate())
        self.ground.setPos(0, 0, 0)
        self.ground.setHpr(0, -90, 0)
        self.ground.setTexture(self.road_texture)

        # Generate the city layout
        self.generate_city()

    def generate_city(self):
        """
        Generates a city layout from a predefined map and sets ground texture scale.
        """
        # Map definition: 0 = road, 1 = building
        city_map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        cell_size = 12
        map_size = len(city_map)
        offset = (map_size * cell_size) / 2.0

        # Scale the ground texture to align with the city grid
        ground_card_size = 200 # as defined in __init__
        num_tiles = ground_card_size / cell_size
        self.ground.setTexScale(TextureStage.getDefault(), num_tiles, num_tiles)

        # Offset the texture to center the intersections on the roads
        tex_offset = 0.5 * (cell_size / ground_card_size)
        self.ground.setTexOffset(TextureStage.getDefault(), tex_offset, tex_offset)

        for y, row in enumerate(city_map):
            for x, cell in enumerate(row):
                if cell == 1:
                    pos_x = x * cell_size - offset + cell_size / 2.0
                    pos_y = y * cell_size - offset + cell_size / 2.0
                    self.create_building(pos_x, pos_y, cell_size)

    def _create_road_texture(self):
        """Generates a procedural road texture for an intersection."""
        img_size = 256
        image = PNMImage(img_size, img_size)
        image.fill(0.18, 0.18, 0.18)  # Sidewalk/gutter color

        road_color = (0.1, 0.1, 0.1)  # Asphalt color
        road_width_px = 128
        road_start_px = (img_size - road_width_px) / 2

        # Draw road cross
        for y in range(img_size):
            for x in range(int(road_start_px), int(road_start_px + road_width_px)):
                image.setXel(x, y, *road_color)
                image.setXel(y, x, *road_color)

        # Dashed yellow lines
        line_color = (0.9, 0.7, 0.2)
        dash_len = 32
        dash_gap = 24
        line_pos = img_size // 2
        for i in range(0, img_size, dash_len + dash_gap):
            for p in range(i, i + dash_len):
                if p < img_size:
                    image.setXel(line_pos - 1, p, *line_color) # Vertical
                    image.setXel(line_pos, p, *line_color)
                    image.setXel(p, line_pos - 1, *line_color) # Horizontal
                    image.setXel(p, line_pos, *line_color)

        tex = Texture()
        tex.load(image)
        tex.setWrapU(Texture.WM_repeat)
        tex.setWrapV(Texture.WM_repeat)
        return tex

    def _create_building_texture(self):
        """Generates a procedural window texture and returns it."""
        img_size_x, img_size_y = 64, 128
        image = PNMImage(img_size_x, img_size_y, 4)
        image.addAlpha()
        image.fill(0.05, 0.05, 0.05)
        image.alpha_fill(1)

        window_color = (0.9, 0.85, 0.6)  # Warm yellow
        window_spacing_x = 16
        window_spacing_y = 24
        window_size_x = 10
        window_size_y = 16

        for y in range(4, img_size_y, window_spacing_y):
            for x in range(4, img_size_x, window_spacing_x):
                if random.random() > 0.4:  # Some windows are dark
                    for win_y in range(y, y + window_size_y):
                        for win_x in range(x, x + window_size_x):
                            if win_x < img_size_x and win_y < img_size_y:
                                image.setXel(win_x, win_y, *window_color)

        tex = Texture()
        tex.load(image)
        tex.setWrapU(Texture.WM_repeat)
        tex.setWrapV(Texture.WM_repeat)
        return tex

    def create_building(self, x, y, size):
        """
        Creates a single building with a collision solid and randomized appearance.
        """
        # Create the visual model
        building = self.base.loader.loadModel("models/box")
        building.reparentTo(self.base.render)
        building.setPos(x, y, 0)

        # Randomize height and color
        building_height = random.uniform(10, 30)
        building_color = random.uniform(0.4, 0.7)
        building.setScale(size / 2.0, size / 2.0, building_height / 2.0)
        building.setColor(building_color, building_color, building_color, 1)
        building.setTexture(self.building_texture)
        self.buildings.append(building)

        # Create the collision solid to match the new height
        half_size = size / 2.0
        c_solid = CollisionBox(Point3(-half_size, -half_size, 0), Point3(half_size, half_size, building_height))
        c_node = CollisionNode('building_collider')
        c_node.addSolid(c_solid)

        # Set this as a static, "from" object that other things collide into
        c_node.setFromCollideMask(BitMask32.bit(1))
        c_node.setIntoCollideMask(BitMask32.allOff())

        building.attachNewNode(c_node)
