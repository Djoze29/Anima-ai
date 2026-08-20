"""
haptics.py
Retour haptique (vibrations) simulant ronronnement / battement de cœur.
Utilise plyer.vibrator, disponible sur Android via Kivy/Buildozer.
"""

try:
    from plyer import vibrator
    HAS_VIBRATOR = True
except Exception:
    HAS_VIBRATOR = False


def pulse(duration=0.1):
    """Vibration courte unique (ex: caresse, tap)."""
    if HAS_VIBRATOR:
        try:
            vibrator.vibrate(duration)
        except Exception:
            pass


def heartbeat_pattern():
    """
    Pattern répété façon battement de cœur.
    Sur Android, vibrator.pattern prend une liste [pause, vibr, pause, vibr, ...] en secondes.
    """
    if HAS_VIBRATOR:
        try:
            pattern = [0, 0.1, 0.1, 0.1, 0.3]
            vibrator.pattern(pattern)
        except Exception:
            pulse(0.1)


def purr_pattern():
    """Pattern continu léger façon ronronnement."""
    if HAS_VIBRATOR:
        try:
            pattern = [0] + [0.05, 0.05] * 8
            vibrator.pattern(pattern)
        except Exception:
            pulse(0.05)
