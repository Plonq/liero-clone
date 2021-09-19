import random
import time

from src.assets import assets
from src.engine.signals import observe


class SoundEffects:
    def __init__(self):
        self.time_of_last_explosion = 0
        observe("small_explosion", self._small_explosion)

    def _small_explosion(self):
        if (
            time.time() - self.time_of_last_explosion
            > 0.2 + random.randint(-10, 10) / 10
        ):
            snd = assets["sound"]["explosions"]["small"]
            snd.set_volume(0.03)
            snd.play()
            self.time_of_last_explosion = time.time()
