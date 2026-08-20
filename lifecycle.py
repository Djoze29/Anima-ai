"""
lifecycle.py
Détecte les transitions importantes (éclosion, évolution, mort) pour
que l'UI puisse réagir (message, popup, animation), en s'appuyant sur
l'état déjà calculé dans creature.py à chaque tick().
"""


class LifecycleManager:
    def __init__(self, creature):
        self.creature = creature
        self._was_egg = creature.is_egg
        self._last_stage_index = creature.stage_index
        self._was_alive = creature.alive

    def poll_events(self):
        """Retourne une liste d'événements survenus depuis le dernier appel."""
        events = []
        c = self.creature

        if self._was_egg and not c.is_egg:
            events.append(("hatched", None))
        self._was_egg = c.is_egg

        if not c.is_egg and c.stage_index > self._last_stage_index:
            events.append(("evolved", c.stage_index))
        self._last_stage_index = c.stage_index

        if self._was_alive and not c.alive:
            events.append(("died", None))
        self._was_alive = c.alive

        return events
