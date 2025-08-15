from panda3d.core import CardMaker, CollisionNode, CollisionBox, Point3, BitMask32

class World:
    def __init__(self, base):
        """
        Initializes the game world, including the ground plane and city.

        :param base: The ShowBase instance.
        """
        self.base = base
        self.buildings = []

        # Set up the ground plane
        cm = CardMaker('ground')
        cm.setFrame(-100, 100, -100, 100)
        self.ground = self.base.render.attachNewNode(cm.generate())
        self.ground.setPos(0, 0, 0)
        self.ground.setHpr(0, -90, 0)
        self.ground.setColor(0.2, 0.2, 0.2, 1)

        # Generate the city layout
        self.generate_city()

    def generate_city(self):
        """
        Generates a city layout from a predefined map.
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

        for y, row in enumerate(city_map):
            for x, cell in enumerate(row):
                if cell == 1:
                    pos_x = x * cell_size - offset + cell_size / 2.0
                    pos_y = y * cell_size - offset + cell_size / 2.0
                    self.create_building(pos_x, pos_y, cell_size)

    def create_building(self, x, y, size):
        """
        Creates a single building with a collision solid.
        """
        # Create the visual model
        building = self.base.loader.loadModel("models/box")
        building.reparentTo(self.base.render)
        building.setPos(x, y, 0)
        building_height = 16
        building.setScale(size / 2.0, size / 2.0, building_height / 2.0)
        building.setColor(0.5, 0.5, 0.5, 1)
        self.buildings.append(building)

        # Create the collision solid
        half_size = size / 2.0
        c_solid = CollisionBox(Point3(-half_size, -half_size, 0), Point3(half_size, half_size, building_height))
        c_node = CollisionNode('building_collider')
        c_node.addSolid(c_solid)

        # Set this as a static, "from" object that other things collide into
        c_node.setFromCollideMask(BitMask32.bit(1))
        c_node.setIntoCollideMask(BitMask32.allOff())

        building.attachNewNode(c_node)
