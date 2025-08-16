from panda3d.core import LVector3, CollisionNode, CollisionCapsule, BitMask32, CardMaker, Texture, PNMImage, NodePath, Point3, CollisionRay, CollisionHandlerQueue, Vec3
from direct.interval.IntervalGlobal import Sequence, LerpColorScaleInterval, Func
from src.vfx import create_boost_effect

class Player:
    def __init__(self, base, sound_manager, spawn_pos):
        self.base = base
        self.sound_manager = sound_manager

        # Suspension Physics
        self.vertical_velocity = 0.0
        self.ride_height = 1.0
        self.spring_strength = 200.0
        self.damping = 20.0
        self.gravity = -9.8

        self.node = self.base.render.attachNewNode("player")
        spawn_pos.setZ(self.ride_height)
        self.node.setPos(spawn_pos)

        self.visuals_node = self.node.attachNewNode("player_visuals")

        # Load the new car model
        try:
            car_model = self.base.loader.loadModel("assets/models/car/scene.gltf")
            car_model.reparentTo(self.visuals_node)
            # Adjust scale and orientation
            car_model.setScale(0.5)
            car_model.setH(180)
            car_model.setP(90)
        except Exception as e:
            print(f"Warning: Could not load car model. Using fallback. Error: {e}")
            # Fallback to procedural car if model fails to load
            chassis = self.base.loader.loadModel("models/box")
            chassis.reparentTo(self.visuals_node)
            chassis.setScale(0.7, 1.2, 0.3)
            chassis.setPos(0, 0, 0)
            chassis.setColor(0.8, 0.1, 0.1, 1)

        self.boost_vfx = create_boost_effect(self.base)
        self.boost_vfx.reparentTo(self.node)
        self.boost_vfx.setPos(0, -1.3, 0.2)
        self.skid_texture = self._create_skid_texture()
        self.skid_timer = 0.0
        self.skid_interval = 0.05
        self.skid_card_maker = CardMaker('skidmark_cm')
        self.skid_card_maker.setFrame(-0.5, 0.5, -1.5, 1.5)

        # Physics and State Variables
        self.current_speed = 0.0
        self.acceleration = 50.0
        self.braking_force = 100.0
        self.friction = 25.0
        self.max_speed = 50.0
        self.max_boost_speed = 80.0
        self.steering_speed = 150.0
        self.top_speed = self.max_boost_speed * 3.5
        self.wanted_level = 0
        self.boost_level = 100.0
        self.was_boosting = False

        # Suspension Ray
        self.ray_node = self.node.attachNewNode(CollisionNode('suspension_ray'))
        self.ray_node.node().addSolid(CollisionRay(0, 0, 0, 0, 0, -1))
        self.ray_node.node().setFromCollideMask(BitMask32.bit(2))
        self.ray_node.node().setIntoCollideMask(BitMask32.allOff())
        self.ray_queue = CollisionHandlerQueue()

        self.keyMap = {"forward": False, "backward": False, "left": False, "right": False, "boost": False}

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

        capsule_height = 0.8
        capsule_radius = 0.7
        p1 = Point3(0, -0.5, capsule_height)
        p2 = Point3(0, 0.5, capsule_height)
        c_solid = CollisionCapsule(p1, p2, capsule_radius)
        self.collider_node = self.node.attachNewNode(CollisionNode('player_collider'))
        self.collider_node.node().addSolid(c_solid)
        self.collider_node.node().setFromCollideMask(BitMask32.allOff())
        self.collider_node.node().setIntoCollideMask(BitMask32.bit(1))

    def _create_skid_texture(self):
        img = PNMImage(64, 128, 4)
        img.addAlpha()
        img.fill(0, 0, 0)
        img.alpha_fill(0)
        img.renderSpot((1, 1, 1, 0.4), (0.5, 0.5, 0.5, 0.0), 60, 30)
        tex = Texture()
        tex.load(img)
        return tex

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def update(self, dt):
        print(self.keyMap)
        is_accelerating = self.keyMap["forward"]
        is_braking = self.keyMap["backward"]
        is_turning = self.keyMap["left"] or self.keyMap["right"]
        is_boosting = self.keyMap["boost"] and self.boost_level > 0

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

        if is_accelerating:
            self.current_speed += self.acceleration * dt
        elif is_braking:
            self.current_speed = max(0, self.current_speed - self.braking_force * dt) if self.current_speed > 0 else min(0, self.current_speed + self.braking_force * dt)
        else:
            if self.current_speed > 0:
                self.current_speed = max(0, self.current_speed - self.friction * dt)
            else:
                self.current_speed = min(0, self.current_speed + self.friction * dt)

        target_max_speed = self.max_boost_speed if is_boosting else self.max_speed
        self.current_speed = max(-self.max_speed * 0.5, min(target_max_speed, self.current_speed))

        is_drifting = is_turning and abs(self.current_speed) > self.max_speed * 0.6
        self.sound_manager.toggle_skid(is_drifting)
        if is_drifting:
            self.current_speed *= 0.99
            self.skid_timer += dt
            if self.skid_timer > self.skid_interval:
                self.skid_timer = 0
                self._create_skid_mark()

        steering_divisor = target_max_speed * 1.5
        if is_boosting:
            steering_divisor *= 2.0
        steering = self.steering_speed * (1.0 - (abs(self.current_speed) / steering_divisor))
        if is_drifting:
            steering *= 1.3
        if self.keyMap["left"]:
            self.node.setH(self.node.getH() + steering * dt)
        if self.keyMap["right"]:
            self.node.setH(self.node.getH() - steering * dt)

        lerp_speed = 10 * dt
        target_pitch = 2 if is_accelerating and self.current_speed > 0 else (-2 if is_braking and self.current_speed > 0 else 0)
        target_roll = 3 if self.keyMap["left"] and self.current_speed != 0 else (-3 if self.keyMap["right"] and self.current_speed != 0 else 0)

        current_p, current_r = self.visuals_node.getP(), self.visuals_node.getR()
        new_p = current_p + lerp_speed * (target_pitch - current_p)
        new_r = current_r + lerp_speed * (target_roll - current_r)
        self.visuals_node.setHpr(self.visuals_node.getH(), new_p, new_r)

        self.node.setY(self.node, self.current_speed * dt)
        self.speed = abs(self.current_speed * 3.5)

        # --- Suspension Logic ---
        self.base.cTrav.traverse(self.base.render)

        ground_z = -1000
        if self.ray_queue.getNumEntries() > 0:
            self.ray_queue.sortEntries()
            ray_hit = self.ray_queue.getEntry(0)
            ground_z = ray_hit.getSurfacePoint(self.base.render).getZ()

        on_ground = self.node.getZ() < ground_z + self.ride_height + 0.1

        if on_ground:
            displacement = self.node.getZ() - (ground_z + self.ride_height)
            spring_force = -displacement * self.spring_strength
            damping_force = -self.vertical_velocity * self.damping
            total_force = spring_force + damping_force
            acceleration = total_force # mass = 1
            self.vertical_velocity += acceleration * dt
        else:
            self.vertical_velocity += self.gravity * dt

        self.node.setZ(self.node.getZ() + self.vertical_velocity * dt)

    def _create_skid_mark(self):
        for side in [-1, 1]:
            skid_np = NodePath(self.skid_card_maker.generate())
            skid_np.setTexture(self.skid_texture)
            skid_np.setTransparency(True)
            skid_np.reparentTo(self.base.render)
            skid_np.setPos(self.node, 0.5 * side, -0.8, 0.01)
            skid_np.setHpr(self.node.getHpr())
            skid_np.setR(-90)

            fade_out = LerpColorScaleInterval(skid_np, 1.5, (1,1,1,0), (1,1,1,0.5))
            destroy = Func(skid_np.removeNode)
            Sequence(fade_out, destroy).start()
