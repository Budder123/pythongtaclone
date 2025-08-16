class SoundManager:
    """
    Manages all game sounds. It is designed to fail gracefully if sound
    files are missing, allowing the game to run without audio assets.
    """
    def __init__(self, base):
        self.base = base
        self.engine_sound = None
        self.boost_sound = None
        self.collision_sound = None
        self.skid_sound = None
        self.is_skidding = False

    def start_engine(self):
        """Starts the looping engine sound."""
        if self.engine_sound and self.engine_sound.status() != self.engine_sound.PLAYING:
            self.engine_sound.play()

    def update(self, player_speed, top_speed):
        """
        Updates the pitch of the engine sound based on player speed.
        """
        if self.engine_sound:
            # We set a base play rate and scale it up with speed
            min_rate = 0.6
            max_rate = 2.2
            if top_speed > 0:
                play_rate = min_rate + (max_rate - min_rate) * (player_speed / top_speed)
                self.engine_sound.setPlayRate(play_rate)
            else:
                self.engine_sound.setPlayRate(min_rate)

    def play_boost(self):
        """Plays the boost sound effect."""
        if self.boost_sound:
            self.boost_sound.play()

    def play_collision(self):
        """Plays the collision sound effect."""
        if self.collision_sound:
            self.collision_sound.stop()
            self.collision_sound.play()

    def toggle_skid(self, is_skidding):
        """Plays or stops the looping skid sound."""
        if self.skid_sound and self.is_skidding != is_skidding:
            self.is_skidding = is_skidding
            if is_skidding:
                self.skid_sound.play()
            else:
                self.skid_sound.stop()
