"""
notifications.py
Rappels locaux ("ton animal a faim") via plyer.notification.

LIMITE IMPORTANTE : plyer.notification affiche une notification
immédiatement quand on l'appelle depuis le code Python en cours
d'exécution — il ne programme PAS une alerte future si l'app est
totalement fermée (tuée). Pour de vraies notifications programmées
qui survivent à la fermeture de l'app, il faudrait un vrai service
Android (AlarmManager / WorkManager via pyjnius), qui est une
prochaine étape possible si ce point est bloquant.

Pour l'instant, cette version déclenche une notification quand
l'app est ouverte et détecte que la créature a besoin d'attention
(faim basse, sale, etc.) — utile si l'app tourne en arrière-plan
Android (pas totalement tuée), moins fiable si le système l'a tuée.
"""

try:
    from plyer import notification
    HAS_NOTIFICATION = True
except Exception:
    HAS_NOTIFICATION = False

import time

_last_notif_time = {}
_COOLDOWN = 3600  # ne pas spammer : 1 notification max par heure et par type


def _can_notify(key):
    now = time.time()
    last = _last_notif_time.get(key, 0)
    if now - last >= _COOLDOWN:
        _last_notif_time[key] = now
        return True
    return False


def notify(title, message, key="general"):
    if not HAS_NOTIFICATION:
        return
    if not _can_notify(key):
        return
    try:
        notification.notify(title=title, message=message, timeout=10)
    except Exception:
        pass


def check_and_notify(creature):
    if creature.is_egg or not creature.alive:
        return
    if creature.hunger < 25:
        notify("Anima AI", f"{creature.name} a faim !", key="hunger")
    if creature.cleanliness < 30:
        notify("Anima AI", f"{creature.name} a besoin d'une douche.", key="clean")
