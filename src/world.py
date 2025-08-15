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
        Generates a more organic city layout using a random walk algorithm.
        """
        map_width, map_height = 20, 20
        self.city_map = [[1 for _ in range(map_width)] for _ in range(map_height)]

        # Drunken walk algorithm to carve roads
        x, y = map_width // 2, map_height // 2
        self.city_map[y][x] = 0
        num_roads = (map_width * map_height) // 3 # Carve out about 1/3 of the map

        for _ in range(num_roads):
            # Move in a random direction
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            x, y = x + dx, y + dy

            # Keep walker within bounds
            x = max(1, min(x, map_width - 2))
            y = max(1, min(y, map_height - 2))

            # Carve road (and make it a bit thicker)
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= y+i < map_height and 0 <= x+j < map_width:
                        # Don't carve the absolute edges of the map
                        if 0 < y+i < map_height-1 and 0 < x+j < map_width-1:
                             self.city_map[y+i][x+j] = 0

        cell_size = 12
        self.map_size = map_width # Assume square map for now
        self.cell_size = cell_size
        offset = (self.map_size * self.cell_size) / 2.0

        # Scale the ground texture to align with the city grid
        ground_card_size = 200 # as defined in __init__
        num_tiles = ground_card_size / cell_size
        self.ground.setTexScale(TextureStage.getDefault(), num_tiles, num_tiles)

        # Offset the texture to center the intersections on the roads
        tex_offset = 0.5 * (cell_size / ground_card_size)
        self.ground.setTexOffset(TextureStage.getDefault(), tex_offset, tex_offset)

        for y, row in enumerate(self.city_map):
            for x, cell in enumerate(row):
                if cell == 1:
                    pos_x = x * self.cell_size - offset + self.cell_size / 2.0
                    pos_y = y * self.cell_size - offset + self.cell_size / 2.0
                    self.create_building(pos_x, pos_y, self.cell_size)

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

    def get_safe_spawn_point(self):
        """Finds the first road tile '0' and returns its world coordinates."""
        offset = (self.map_size * self.cell_size) / 2.0
        for y, row in enumerate(self.city_map):
            for x, cell in enumerate(row):
                if cell == 0:
                    pos_x = x * self.cell_size - offset + self.cell_size / 2.0
                    pos_y = y * self.cell_size - offset + self.cell_size / 2.0
                    return Point3(pos_x, pos_y, 0.5) # Return as a Point3 object
        return Point3(0, 0, 0.5) # Fallback, though should not be reached

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
