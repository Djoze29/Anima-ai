# Anima AI (Chrono-Fauna)

Tamagotchi nouvelle génération : choisis parmi 10 créatures aux
silhouettes distinctes, prends-en soin sur un rythme réaliste
(heures/jours, pas secondes), regarde-la grandir d'œuf à créature
mature, garde-la propre, apprends-lui des mots, et attention — si
tu la négliges plus de 2 jours, elle meurt et il faut recommencer.

## Nouveautés v2

- **Sélection de créature** : 10 espèces (dragon, félin, alien, oiseau,
  aquatique, lapin, ours, robot, fantôme, plante), silhouettes
  vraiment différentes (oreilles, ailes, cornes, nageoires, etc.)
- **Rythme réaliste** : faim gérée sur un cycle d'environ 3h, jeu
  limité à quelques fois par jour, propreté qui se dégrade sur ~2 jours
- **Cycle de vie complet** : œuf (~1.5 jour) → éclosion → évolution
  tous les 3 jours au début, puis 5, puis 7 jours (ralentissement
  progressif)
- **Propreté** : caca aléatoire, bouton Nettoyer, la créature devient
  visiblement sale si négligée
- **Mort par négligence** : plus de 2 jours sans manger = fin de partie,
  retour à l'écran de sélection
- **Apprentissage de mots** : champ de texte pour enseigner des mots,
  comptabilisés dans le profil de la créature
- **Notifications de rappel** : alerte si faim basse ou créature sale
  (limite : fiable seulement si l'app tourne encore en arrière-plan,
  pas si elle est totalement tuée par le système — une vraie alarme
  Android nécessiterait un développement supplémentaire)

## Prochaines étapes (pas encore faites)

- Vrai système d'apprentissage du langage (la créature "lit" les mots)
- Multijoueur Bluetooth local entre deux téléphones
- Notifications programmées fiables même app fermée (AlarmManager)

## Structure

- `main.py` — app Kivy, écrans (sélection / jeu), rendu, UI
- `species.py` — les 10 espèces sélectionnables et leurs silhouettes
- `creature.py` — état interne, rythme réaliste, âge/évolution, mort
- `ai_behavior.py` — humeur affichée selon les stats
- `sensors.py` — luminosité, micro (placeholder)
- `haptics.py` — vibrations
- `lifecycle.py` — détection des événements (éclosion, évolution, mort)
- `notifications.py` — rappels locaux via plyer
- `buildozer.spec` — config de compilation Android
- `.github/workflows/build.yml` — build automatique (ou build via Arena
  si GitHub Actions échoue sur des bugs d'écosystème Buildozer)

## Comment obtenir l'APK

1. Pousse ce dossier sur GitHub (branche `main`).
2. GitHub Actions ou un agent Arena.ai (Agent Mode) compile l'APK.
3. Récupère le `.apk` généré et installe-le sur ton téléphone.
