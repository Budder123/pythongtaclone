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
        img_size_x, img_size_y = 64, 128
        image = PNMImage(img_size_x, img_size_y, 4)
        image.addAlpha()
        image.fill(0.05, 0.05, 0.05)
        image.alpha_fill(1)
        window_color = (0.9, 0.85, 0.6)
        for y in range(4, img_size_y, 24):
            for x in range(4, img_size_x, 16):
                if random.random() > 0.4:
                    for win_y in range(y, y + 16):
                        for win_x in range(x, x + 10):
                            if win_x < img_size_x and win_y < img_size_y:
                                image.setXel(win_x, win_y, *window_color)
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
        building.setPos(x, y, 0)
        building_height = random.uniform(15, 40)
        building_color = random.uniform(0.4, 0.7)
        building.setScale(width / 2.0, depth / 2.0, building_height / 2.0)
        building.setColor(building_color, building_color, building_color, 1)
        building.setTexture(self.building_texture)
        self.buildings.append(building)
        c_solid = CollisionBox(Point3(-width/2, -depth/2, 0), Point3(width/2, depth/2, building_height))
        c_node = CollisionNode('building_collider')
        c_node.addSolid(c_solid)
        c_node.setFromCollideMask(BitMask32.bit(1))
        c_node.setIntoCollideMask(BitMask32.allOff())
        building.attachNewNode(c_node)
