import random
import time

from src.assets import assets
from src.engine.signals import observe


class SoundEffects:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.time_of_last_explosion = 0
        self.queue = set()
        observe("small_explosion", self._small_explosion)
        observe("gunshot", self._gunshot)
        observe("worm_died", self._death)

    def update(self, dt):
        for snd in self.queue:
            snd.play()
        self.queue.clear()

    def _small_explosion(self):
        if (
            time.time() - self.time_of_last_explosion
            > 0.4 + random.randint(-10, 10) / 10
        ):
            snd = assets["sound"]["explosions"][random.randint(2, 3)]
            snd.set_volume(0.07)
            self.queue.add(snd)
            self.time_of_last_explosion = time.time()

    def _gunshot(self, worm):
        snd = assets["sound"]["gunshots"][5]
        snd.set_volume(0.03)
        self.queue.add(snd)

    def _death(self, worm):
        snd = assets["sound"]["death"]
        snd.set_volume(0.4)
        self.queue.add(snd)
