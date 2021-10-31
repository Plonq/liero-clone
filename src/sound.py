import math
import random
import time

from src.config import config
from src.assets import assets
from src.engine.signals import observe
from src.engine.utils import throttle


class SoundEffects:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.queue = set()
        observe("small_explosion", self._small_explosion)
        observe("weapon_fired", self._weapon_fired)
        observe("worm_died", self._death)
        observe("worm_damaged", self._worm_damaged)
        observe("worm_impact", self._worm_impact)
        observe("grapple_launched", self._grapple_launched)

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

    @throttle(timeout_ms=500, variance=500)
    def _small_explosion(self, position):
        snd = assets["sound"]["explosions"][random.randint(1, 2)]
        snd.set_volume(0.07)
        self.queue.add(SoundDef(snd, position))

    def _weapon_fired(self, weapon):
        if weapon.name == "minigun":
            snd = assets["sound"]["gunshots"][2]
            snd.set_volume(0.03)
            self.queue.add(SoundDef(snd, weapon.owner.position))

        elif weapon.name == "shotgun":
            snd = assets["sound"]["gunshots"][3]
            snd.set_volume(0.1)
            self.queue.add(SoundDef(snd, weapon.owner.position))

        elif weapon.name == "missile":
            snd = assets["sound"]["explosions"][1]
            snd.set_volume(0.1)
            self.queue.add(SoundDef(snd, weapon.owner.position))

        elif weapon.name == "sniper":
            snd = assets["sound"]["gunshots"][1]
            snd.set_volume(0.5)
            self.queue.add(SoundDef(snd, weapon.owner.position))

    def _death(self, worm, killer):
        snd = assets["sound"]["death"]
        snd.set_volume(0.4)
        self.queue.add(SoundDef(snd, worm.position))

    @throttle(timeout_ms=600, variance=1000)
    def _worm_damaged(self, dmg, worm):
        snd = assets["sound"]["grunt"]
        snd.set_volume(0.05)
        self.queue.add(SoundDef(snd, worm.position))

    def _worm_impact(self, worm):
        snd = assets["sound"]["worm-impact"]
        snd.set_volume(0.3)
        self.queue.add(SoundDef(snd, worm.position))

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
