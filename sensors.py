"""
sensors.py
Accès aux capteurs du téléphone (luminosité, micro) via plyer.
Sur PC / environnement de test, retombe sur des valeurs simulées
pour que le reste de l'app tourne quand même sans capteurs réels.
"""

try:
    from plyer import light
    HAS_LIGHT = True
except Exception:
    HAS_LIGHT = False

import random


class SensorManager:
    def __init__(self, on_light_update=None, on_voice_update=None):
        self.on_light_update = on_light_update
        self.on_voice_update = on_voice_update
        self._light_enabled = False

    def start_light_sensor(self):
        if HAS_LIGHT:
            try:
                light.enable()
                self._light_enabled = True
            except Exception:
                self._light_enabled = False

    def stop_light_sensor(self):
        if HAS_LIGHT and self._light_enabled:
            try:
                light.disable()
            except Exception:
                pass

    def read_light_level(self):
        """Retourne un niveau normalisé 0.0 (noir) à 1.0 (très lumineux)."""
        if HAS_LIGHT and self._light_enabled:
            try:
                lux = light.illumination
                if lux is not None:
                    # Normalisation approximative (0 - 1000 lux -> 0 - 1)
                    return max(0.0, min(1.0, lux / 1000.0))
            except Exception:
                pass
        # Fallback simulé (utile pour tester sans capteur / sur PC)
        return random.uniform(0.3, 0.6)

    def read_microphone_level(self):
        """
        Placeholder : la capture micro réelle nécessite une lib audio
        (ex: audiostream) et des permissions Android (RECORD_AUDIO).
        Retourne (is_soft, volume) simulés pour l'instant.
        À remplacer par une vraie analyse audio dans une itération suivante.
        """
        volume = random.uniform(0.0, 1.0)
        is_soft = volume < 0.4
        return is_soft, volume
