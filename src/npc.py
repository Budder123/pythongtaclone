import random
from panda3d.core import LVector3, NodePath, Point3

def _random_color_component():
    """Helper function to get a random color component for the NPC cars."""
    return 0.3 + 0.5 * random.random()

class NPC:
    def __init__(self, base, world, spawn_pos):
        self.base = base
        self.world = world

        self.node = self.base.render.attachNewNode("npc")
        self.node.setPos(spawn_pos)

        # For now, NPCs will be simple colored boxes.
        npc_model = self.base.loader.loadModel("models/box")
        npc_model.reparentTo(self.node)
        npc_model.setScale(0.7, 1.2, 0.3)
        npc_model.setPos(0, 0, 0.5)

        # Give NPCs a random color
        color = (_random_color_component(), _random_color_component(), _random_color_component(), 1)
        npc_model.setColor(color)

        # Physics and AI State
        self.max_speed = random.uniform(15, 25)
        self.current_speed = self.max_speed
        self.steering_speed = random.uniform(40, 60)

        # AI: Waypoint navigation using grid positions
        self.target_grid_pos = random.choice(self.world.waypoint_nodes)
        self.arrival_threshold = self.world.cell_size / 2.0

    def update(self, dt):
        """Drives the NPC along the waypoint network."""
        if self.target_grid_pos is None:
            return

        target_world_pos = self.world.grid_to_world_map[self.target_grid_pos]

        # --- Waypoint Arrival Check ---
        dist_to_target = (target_world_pos - self.node.getPos()).length()
        if dist_to_target < self.arrival_threshold:
            # Arrived, find next waypoint
            connections = self.world.waypoints.get(self.target_grid_pos)
            if connections:
                self.target_grid_pos = random.choice(connections)
            else:
                # This can happen if an NPC gets stuck, pick a new random one
                self.target_grid_pos = random.choice(self.world.waypoint_nodes)

            # Update the world position as well
            target_world_pos = self.world.grid_to_world_map[self.target_grid_pos]

        # --- Steering Logic ---
        # Vector to the target
        vec_to_target = target_world_pos - self.node.getPos()
        vec_to_target.z = 0 # We only care about 2D steering
        vec_to_target.normalize()

        # NPC's forward vector
        forward_vec = self.node.getQuat().getForward()
        forward_vec.z = 0
        forward_vec.normalize()

        # Angle between forward vector and target vector
        angle = forward_vec.signedAngleRad(vec_to_target, LVector3.up())

        # Apply steering
        # Clamp the angle to a reasonable range to avoid over-steering
        steer_amount = angle * self.steering_speed * dt
        max_steer = self.steering_speed * dt
        steer_amount = max(min(steer_amount, max_steer), -max_steer)

        self.node.setH(self.node.getH() - steer_amount)

        # --- Movement ---
        self.node.setY(self.node, self.current_speed * dt)
