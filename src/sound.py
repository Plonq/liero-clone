import math
import random
import time

from src.config import config
from src.assets import assets
from src.engine.signals import observe


class SoundEffects:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.queue = set()
        observe("small_explosion", self._small_explosion)
        observe("weapon_fired", self._weapon_fired)
        observe("worm_died", self._death)
        observe("worm_damaged", self._worm_damaged)
        observe("grapple_launched", self._grapple_launched)
        # Throttling
        self.time_of_last_explosion = 0
        self.time_of_last_grunt = 0

    def update(self, dt):
        for sound_def in self.queue:
            self._play_effect(sound_def)
        self.queue.clear()

    def _play_effect(self, sound_def):
        master_vol = config["settings"]["sound"]["master_volume"]
        effects_vol = config["settings"]["sound"]["effects_volume"]
        if sound_def.position is None:
            distance_multiplier = 1
        else:
            dist_to_source = sound_def.position.distance_to(self.player.position)
            max_distance = math.sqrt(
                pow(self.game.display_size[0], 2) + pow(self.game.display_size[1], 2)
            )
            distance_multiplier = (
                1 - (((dist_to_source - 0.01) * 0.9) / max_distance) + 0.05
            )
        sound_def.adjust_volume(effects_vol * master_vol * distance_multiplier)
        sound_def.play()

    def _small_explosion(self, position):
        if (
            time.time() - self.time_of_last_explosion
            > 0.4 + random.randint(-10, 10) / 10
        ):
            snd = assets["sound"]["explosions"][random.randint(2, 3)]
            snd.set_volume(0.07)
            self.queue.add(SoundDef(snd, position))
            self.time_of_last_explosion = time.time()

    def _weapon_fired(self, weapon):
        if weapon.name == "minigun":
            snd = assets["sound"]["gunshots"][5]
            snd.set_volume(0.03)
            self.queue.add(SoundDef(snd, weapon.owner.position))

        elif weapon.name == "shotgun":
            snd = assets["sound"]["gunshots"][7]
            snd.set_volume(0.1)
            self.queue.add(SoundDef(snd, weapon.owner.position))

    def _death(self, worm):
        snd = assets["sound"]["death"]
        snd.set_volume(0.4)
        self.queue.add(SoundDef(snd, worm.position))

    def _worm_damaged(self, dmg, worm):
        snd = assets["sound"]["grunts"][1]
        if time.time() - self.time_of_last_grunt > 0.6 + random.randint(-10, 10) / 10:
            snd.set_volume(0.05)
            self.queue.add(SoundDef(snd, worm.position))
            self.time_of_last_grunt = time.time()

    def _grapple_launched(self, grapple):
        snd = assets["sound"]["slash"]
        snd.set_volume(0.2)
        self.queue.add(SoundDef(snd, grapple.position))


class SoundDef:
    def __init__(self, sound, position):
        self.sound = sound
        self.position = position

    def adjust_volume(self, multiplier):
        self.sound.set_volume(self.sound.get_volume() * multiplier)

    def play(self):
        self.sound.play()

    def __eq__(self, other):
        return self.sound == other

    def __hash__(self):
        return hash(self.sound)
