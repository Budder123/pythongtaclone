from panda3d.core import CardMaker, CollisionNode, CollisionBox, Point3, BitMask32, PNMImage, Texture, TextureStage
import random

class World:
    def __init__(self, base):
        self.base = base
        self.buildings = []
        self.building_texture = self._create_building_texture()
        self.road_texture = self._create_road_texture()

        cm = CardMaker('ground')
        cm.setFrame(-150, 150, -150, 150)
        self.ground = self.base.render.attachNewNode(cm.generate())
        self.ground.setPos(0, 0, 0)
        self.ground.setHpr(0, -90, 0)
        self.ground.setTexture(self.road_texture)

        self.generate_city()
        self._generate_waypoints()

    def _grid_to_world(self, x, y):
        """Converts grid coordinates to world coordinates."""
        offset_x = (self.map_size_x * self.cell_size) / 2.0
        offset_y = (self.map_size_y * self.cell_size) / 2.0
        pos_x = x * self.cell_size - offset_x + self.cell_size / 2.0
        pos_y = y * self.cell_size - offset_y + self.cell_size / 2.0
        return Point3(pos_x, pos_y, 0.5)

    def _generate_waypoints(self):
        """Generates a waypoint graph from the road sections of the city map."""
        self.grid_to_world_map = {}
        # First, map grid coordinates to world positions for all road cells
        for y, row in enumerate(self.city_map):
            for x, cell in enumerate(row):
                if cell == 0:
                    self.grid_to_world_map[(x, y)] = self._grid_to_world(x, y)

        self.waypoints = {grid_pos: [] for grid_pos in self.grid_to_world_map.keys()}

        # Now, connect adjacent waypoints using grid coordinates
        for (x, y) in self.grid_to_world_map.keys():
            # Check neighbors
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor_grid_pos = (x + dx, y + dy)
                if neighbor_grid_pos in self.grid_to_world_map:
                    self.waypoints[(x, y)].append(neighbor_grid_pos)

        # For easier random access by NPCs
        self.waypoint_nodes = list(self.grid_to_world_map.keys())


    def generate_city(self):
        """
        Generates a city layout from a predefined, static map.
        """
        # A handcrafted map. 0=road, 1=building block
        self.city_map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
            [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        cell_size = 15 # Larger cells for a more spacious feel
        self.map_size_y = len(self.city_map)
        self.map_size_x = len(self.city_map[0]) if self.map_size_y > 0 else 0
        self.cell_size = cell_size

        offset_x = (self.map_size_x * self.cell_size) / 2.0
        offset_y = (self.map_size_y * self.cell_size) / 2.0

        ground_card_size = 300
        num_tiles_x = ground_card_size / cell_size
        num_tiles_y = ground_card_size / cell_size
        self.ground.setTexScale(TextureStage.getDefault(), num_tiles_x, num_tiles_y)

        tex_offset_u = 0.5 * (cell_size / ground_card_size)
        tex_offset_v = 0.5 * (cell_size / ground_card_size)
        self.ground.setTexOffset(TextureStage.getDefault(), tex_offset_u, tex_offset_v)

        for y, row in enumerate(self.city_map):
            for x, cell in enumerate(row):
                if cell == 1:
                    pos_x = x * self.cell_size - offset_x + self.cell_size / 2.0
                    pos_y = y * self.cell_size - offset_y + self.cell_size / 2.0
                    self.create_building(pos_x, pos_y, self.cell_size, self.cell_size)

    def _create_road_texture(self):
        img_size = 256
        image = PNMImage(img_size, img_size)
        image.fill(0.18, 0.18, 0.18)
        road_color = (0.1, 0.1, 0.1)
        road_width_px = 128
        road_start_px = (img_size - road_width_px) / 2
        for y in range(img_size):
            for x in range(int(road_start_px), int(road_start_px + road_width_px)):
                image.setXel(x, y, *road_color)
                image.setXel(y, x, *road_color)
        line_color = (0.9, 0.7, 0.2)
        dash_len = 32
        dash_gap = 24
        line_pos = img_size // 2
        for i in range(0, img_size, dash_len + dash_gap):
            for p in range(i, i + dash_len):
                if p < img_size:
                    image.setXel(line_pos - 1, p, *line_color)
                    image.setXel(line_pos, p, *line_color)
                    image.setXel(p, line_pos - 1, *line_color)
                    image.setXel(p, line_pos, *line_color)
        tex = Texture()
        tex.load(image)
        tex.setWrapU(Texture.WM_repeat)
        tex.setWrapV(Texture.WM_repeat)
        return tex

    def _create_building_texture(self):
        img_size_x, img_size_y = 128, 256
        image = PNMImage(img_size_x, img_size_y, 4)
        image.addAlpha()

        # Base white color
        image.fill(1, 1, 1)

        image.alpha_fill(1)

        # Window properties
        win_width, win_height = 10, 18
        win_h_spacing, win_v_spacing = 18, 32

        # Draw windows
        for y in range(win_v_spacing // 2, img_size_y - win_v_spacing, win_v_spacing):
            for x in range(win_h_spacing // 2, img_size_x - win_h_spacing, win_h_spacing):
                # Decide if window is lit
                is_lit = random.random() > 0.6
                win_color = (0.7, 0.85, 1.0) if is_lit else (0.1, 0.1, 0.12)

                # Draw window pane
                for iy in range(y, y + win_height):
                    for ix in range(x, x + win_width):
                        if ix < img_size_x and iy < img_size_y:
                            image.setXel(ix, iy, *win_color)

                # Draw subtle window frame
                frame_color = (0.05, 0.05, 0.05)
                for ix in range(x - 1, x + win_width + 1):
                     if 0 <= ix < img_size_x:
                        if 0 <= y-1 < img_size_y: image.setXel(ix, y - 1, *frame_color)
                        if 0 <= y+win_height < img_size_y: image.setXel(ix, y + win_height, *frame_color)
                for iy in range(y - 1, y + win_height + 1):
                    if 0 <= iy < img_size_y:
                        if 0 <= x-1 < img_size_x: image.setXel(x - 1, iy, *frame_color)
                        if 0 <= x+win_width < img_size_x: image.setXel(x + win_width, iy, *frame_color)

        tex = Texture()
        tex.load(image)
        tex.setWrapU(Texture.WM_repeat)
        tex.setWrapV(Texture.WM_repeat)
        return tex

    def get_safe_spawn_point(self):
        offset_x = (self.map_size_x * self.cell_size) / 2.0
        offset_y = (self.map_size_y * self.cell_size) / 2.0
        for y, row in enumerate(self.city_map):
            for x, cell in enumerate(row):
                if cell == 0:
                    pos_x = x * self.cell_size - offset_x + self.cell_size / 2.0
                    pos_y = y * self.cell_size - offset_y + self.cell_size / 2.0
                    return Point3(pos_x, pos_y, 0.5)
        return Point3(0, 0, 0.5)

    def create_building(self, x, y, width, depth):
        building = self.base.loader.loadModel("models/box")
        building.reparentTo(self.base.render)
        building_height = random.uniform(15, 40)
        # Set Z to a small positive value to avoid both sinking and floating artifacts
        building.setPos(x, y, 0.5)
        building.setScale(width / 2.0, depth / 2.0, building_height / 2.0)
        building.setColor(1, 1, 1, 1) # Ensure model is white
        building.setTexture(self.building_texture)
        building.setTexScale(TextureStage.getDefault(), width / 10, building_height / 10)
        self.buildings.append(building)
        # Create a unit collision box that matches the "models/box" model.
        # It will be automatically scaled by the building's scale.
        c_solid = CollisionBox(Point3(-1, -1, -1), Point3(1, 1, 1))
        c_node = CollisionNode('building_collider')
        c_node.addSolid(c_solid)
        c_node.setFromCollideMask(BitMask32.bit(1))
        c_node.setIntoCollideMask(BitMask32.allOff())
        building.attachNewNode(c_node)
