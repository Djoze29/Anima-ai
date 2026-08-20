"""
creature.py
État interne de la créature Anima AI — v2.

Rythmes réalistes basés sur le temps réel écoulé (time.time()), pas
sur des secondes de jeu : nourrir toutes les ~3h, jouer réparti sur
la journée, évolution sur plusieurs jours, mort si négligée plus de
2 jours.
"""

import time
import json
import os
import random

SAVE_FILE = "creature_save.json"

# --- Constantes de rythme (en secondes réelles) ---
HOUR = 3600
DAY = 24 * HOUR

FEED_INTERVAL = 3 * HOUR          # doit manger environ toutes les 3h
PLAY_WINDOW = DAY                 # jouer réparti sur la journée
DEATH_NEGLECT_THRESHOLD = 2 * DAY  # mort si pas nourri depuis 2 jours

EGG_DURATION = 1.5 * DAY          # reste œuf ~1.5 jour
POOP_INTERVAL_MIN = 4 * HOUR
POOP_INTERVAL_MAX = 10 * HOUR
DIRTY_AFTER_POOP_COUNT = 3        # devient "sale" après 3 cacas non nettoyés

# Intervalles d'évolution par palier (en jours), qui s'allongent avec l'âge
EVOLUTION_SCHEDULE = [3, 3, 3, 5, 5, 7, 7, 7]  # jours entre chaque évolution


class Creature:
    def __init__(self, species_id="dragonet", name="Anima"):
        self.species_id = species_id
        self.name = name

        self.hunger = 80.0
        self.energy = 80.0
        self.affection = 50.0
        self.stress = 10.0
        self.cleanliness = 100.0

        self.stage_index = 0          # position dans EVOLUTION_SCHEDULE (0 = juste éclos)
        self.is_egg = True
        self.alive = True

        self.birth_time = time.time()      # moment de la ponte (début de l'œuf)
        self.hatch_time = None             # rempli à l'éclosion
        self.last_evolution_time = None    # rempli à l'éclosion

        self.last_update = time.time()
        self.last_interaction = time.time()
        self.last_fed = time.time()
        self.last_played = time.time()
        self.last_cleaned = time.time()
        self.next_poop_time = time.time() + random.uniform(POOP_INTERVAL_MIN, POOP_INTERVAL_MAX)

        self.poop_count = 0
        self.play_count_today = 0
        self.play_day_marker = self._day_index()

        self.color = (0.6, 0.85, 1.0)
        self.traits = {"playful": 0.5, "brave": 0.5}

        self.vocabulary = []  # mots appris (Phase 2)

    # ---------- Utilitaires temps ----------

    def _day_index(self):
        return int(time.time() // DAY)

    def age_seconds(self):
        return time.time() - self.birth_time

    def age_days(self):
        return self.age_seconds() / DAY

    # ---------- Cycle de vie ----------

    def update_stage(self):
        if self.is_egg:
            if self.age_seconds() >= EGG_DURATION:
                self.is_egg = False
                self.hatch_time = time.time()
                self.last_evolution_time = time.time()
            return

        if self.last_evolution_time is None:
            self.last_evolution_time = time.time()
            return

        idx = min(self.stage_index, len(EVOLUTION_SCHEDULE) - 1)
        interval = EVOLUTION_SCHEDULE[idx] * DAY
        if time.time() - self.last_evolution_time >= interval:
            self.stage_index += 1
            self.last_evolution_time = time.time()

    def stage_name(self):
        if self.is_egg:
            return "egg"
        names = ["hatchling", "juvenile", "young", "adult", "mature", "elder"]
        i = min(self.stage_index, len(names) - 1)
        return names[i]

    # ---------- Mise à jour périodique ----------

    def tick(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        if not self.alive:
            return

        self.update_stage()

        if self.is_egg:
            self._update_color()
            return

        # Décroissance lente, calée sur le cycle "toutes les 3h"
        hunger_rate = 100.0 / FEED_INTERVAL  # perd 100 points sur un cycle complet
        self.hunger = max(0.0, self.hunger - dt * hunger_rate)

        energy_rate = 100.0 / (2 * FEED_INTERVAL)
        self.energy = max(0.0, self.energy - dt * energy_rate)

        cleanliness_rate = 100.0 / (2 * DAY)
        self.cleanliness = max(0.0, self.cleanliness - dt * cleanliness_rate)

        if self.hunger < 30 or self.cleanliness < 30:
            self.stress = min(100.0, self.stress + dt * 0.05)
        else:
            self.stress = max(0.0, self.stress - dt * 0.01)

        idle_time = now - self.last_interaction
        if idle_time > 12 * HOUR:
            self.affection = max(0.0, self.affection - dt * 0.005)

        # Caca aléatoire
        if now >= self.next_poop_time:
            self.poop_count += 1
            self.next_poop_time = now + random.uniform(POOP_INTERVAL_MIN, POOP_INTERVAL_MAX)
        if self.poop_count >= DIRTY_AFTER_POOP_COUNT:
            self.cleanliness = min(self.cleanliness, 25.0)

        # Reset du compteur de jeu quotidien
        day_now = self._day_index()
        if day_now != self.play_day_marker:
            self.play_day_marker = day_now
            self.play_count_today = 0

        # Mort si négligé trop longtemps
        if now - self.last_fed >= DEATH_NEGLECT_THRESHOLD:
            self.alive = False

        self._update_color()

    def _update_color(self):
        from species import get_species
        base = get_species(self.species_id)["color"]
        a = self.affection / 100.0
        self.color = (
            min(1.0, base[0] + 0.15 * a),
            min(1.0, base[1] + 0.1 * a),
            min(1.0, base[2] + 0.05 * a),
        )

    # ---------- Actions du joueur ----------

    def feed(self):
        if not self.alive or self.is_egg:
            return False
        self.hunger = min(100.0, self.hunger + 35)
        self.affection = min(100.0, self.affection + 2)
        self.last_fed = time.time()
        self.last_interaction = time.time()
        return True

    def play(self):
        if not self.alive or self.is_egg:
            return False
        if self.play_count_today >= 4:
            return False  # déjà bien joué aujourd'hui
        self.play_count_today += 1
        self.affection = min(100.0, self.affection + 5)
        self.energy = max(0.0, self.energy - 8)
        self.traits["playful"] = min(1.0, self.traits["playful"] + 0.02)
        self.last_played = time.time()
        self.last_interaction = time.time()
        return True

    def pet(self):
        if not self.alive:
            return False
        self.affection = min(100.0, self.affection + 3)
        self.stress = max(0.0, self.stress - 5)
        self.last_interaction = time.time()
        return True

    def rest(self):
        if not self.alive or self.is_egg:
            return False
        self.energy = min(100.0, self.energy + 20)
        self.last_interaction = time.time()
        return True

    def clean(self):
        if not self.alive:
            return False
        self.cleanliness = 100.0
        self.poop_count = 0
        self.stress = max(0.0, self.stress - 3)
        self.last_cleaned = time.time()
        self.last_interaction = time.time()
        return True

    def scare(self):
        self.stress = min(100.0, self.stress + 15)
        self.traits["brave"] = max(0.0, self.traits["brave"] - 0.03)

    def teach_word(self, word):
        word = word.strip().lower()
        if word and word not in self.vocabulary:
            self.vocabulary.append(word)
            self.affection = min(100.0, self.affection + 1)
            return True
        return False

    # ---------- Sauvegarde ----------

    def to_dict(self):
        return {
            "species_id": self.species_id,
            "name": self.name,
            "hunger": self.hunger,
            "energy": self.energy,
            "affection": self.affection,
            "stress": self.stress,
            "cleanliness": self.cleanliness,
            "stage_index": self.stage_index,
            "is_egg": self.is_egg,
            "alive": self.alive,
            "birth_time": self.birth_time,
            "hatch_time": self.hatch_time,
            "last_evolution_time": self.last_evolution_time,
            "last_fed": self.last_fed,
            "last_played": self.last_played,
            "last_cleaned": self.last_cleaned,
            "next_poop_time": self.next_poop_time,
            "poop_count": self.poop_count,
            "play_count_today": self.play_count_today,
            "play_day_marker": self.play_day_marker,
            "traits": self.traits,
            "vocabulary": self.vocabulary,
        }

    def save(self, path=SAVE_FILE):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load(cls, path=SAVE_FILE):
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            data = json.load(f)
        c = cls(species_id=data.get("species_id", "dragonet"), name=data.get("name", "Anima"))
        c.hunger = data.get("hunger", c.hunger)
        c.energy = data.get("energy", c.energy)
        c.affection = data.get("affection", c.affection)
        c.stress = data.get("stress", c.stress)
        c.cleanliness = data.get("cleanliness", c.cleanliness)
        c.stage_index = data.get("stage_index", c.stage_index)
        c.is_egg = data.get("is_egg", c.is_egg)
        c.alive = data.get("alive", c.alive)
        c.birth_time = data.get("birth_time", c.birth_time)
        c.hatch_time = data.get("hatch_time", c.hatch_time)
        c.last_evolution_time = data.get("last_evolution_time", c.last_evolution_time)
        c.last_fed = data.get("last_fed", c.last_fed)
        c.last_played = data.get("last_played", c.last_played)
        c.last_cleaned = data.get("last_cleaned", c.last_cleaned)
        c.next_poop_time = data.get("next_poop_time", c.next_poop_time)
        c.poop_count = data.get("poop_count", c.poop_count)
        c.play_count_today = data.get("play_count_today", c.play_count_today)
        c.play_day_marker = data.get("play_day_marker", c.play_day_marker)
        c.traits = data.get("traits", c.traits)
        c.vocabulary = data.get("vocabulary", c.vocabulary)
        return c

    @classmethod
    def delete_save(cls, path=SAVE_FILE):
        if os.path.exists(path):
            os.remove(path)
