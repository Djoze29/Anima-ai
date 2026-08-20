"""
ai_behavior.py
Machine à états simple qui détermine l'humeur/comportement affiché
de la créature à partir de ses stats internes (creature.py).
"""

MOODS = ["calm", "playful", "hungry", "tired", "scared", "affectionate", "dirty", "egg"]


class BehaviorAI:
    def __init__(self, creature):
        self.creature = creature
        self.current_mood = "calm"
        self.mood_history = []

    def evaluate(self):
        c = self.creature

        if c.is_egg:
            mood = "egg"
        elif c.stress > 70:
            mood = "scared"
        elif c.cleanliness < 30:
            mood = "dirty"
        elif c.hunger < 25:
            mood = "hungry"
        elif c.energy < 20:
            mood = "tired"
        elif c.affection > 75 and c.traits["playful"] > 0.6:
            mood = "playful"
        elif c.affection > 60:
            mood = "affectionate"
        else:
            mood = "calm"

        self.current_mood = mood
        self.mood_history.append(mood)
        if len(self.mood_history) > 50:
            self.mood_history.pop(0)

        return mood

    def reaction_to_voice(self, is_soft, volume):
        c = self.creature
        if c.is_egg:
            return
        if is_soft:
            c.stress = max(0.0, c.stress - 3)
            c.affection = min(100.0, c.affection + 1)
            c.traits["brave"] = min(1.0, c.traits["brave"] + 0.01)
        else:
            if volume > 0.8:
                c.scare()
            else:
                c.traits["playful"] = min(1.0, c.traits["playful"] + 0.01)

    def reaction_to_light(self, lux):
        c = self.creature
        if lux < 0.15:
            c.energy = min(100.0, c.energy + 0.05)
        elif lux > 0.85:
            c.stress = min(100.0, c.stress + 0.5)

    def get_animation_state(self):
        mapping = {
            "calm": "idle",
            "playful": "bounce",
            "hungry": "look_for_food",
            "tired": "yawn",
            "scared": "shake",
            "affectionate": "nuzzle",
            "dirty": "grumble",
            "egg": "wobble",
        }
        return mapping.get(self.current_mood, "idle")
