"""
species.py
Définit les 10 créatures sélectionnables. Chaque espèce a une couleur
de base et une silhouette distincte (ajouts dessinés par-dessus le
corps commun : oreilles, ailes, cornes, queue, etc.) pour que les
personnages soient vraiment différents à l'œil, pas juste recolorés.
"""

SPECIES = [
    {
        "id": "dragonet",
        "name": "Dragonet",
        "color": (0.55, 0.85, 0.45),
        "features": ["wings", "tail_spikes", "horns"],
        "tagline": "Petit dragon curieux et joueur",
    },
    {
        "id": "felin",
        "name": "Félin",
        "color": (0.95, 0.75, 0.35),
        "features": ["ears_cat", "tail_long", "whiskers"],
        "tagline": "Malin, indépendant, câlin sur ses propres termes",
    },
    {
        "id": "alien",
        "name": "Xéno",
        "color": (0.6, 0.4, 0.9),
        "features": ["antenna", "elongated_head"],
        "tagline": "Venu d'ailleurs, curieux de tout",
    },
    {
        "id": "oiseau",
        "name": "Plumo",
        "color": (0.35, 0.65, 0.95),
        "features": ["beak", "wings_small", "crest"],
        "tagline": "Chanteur, léger, toujours en mouvement",
    },
    {
        "id": "aquatique",
        "name": "Bulline",
        "color": (0.25, 0.75, 0.85),
        "features": ["fins", "gills", "tail_fish"],
        "tagline": "Calme et fluide, aime l'eau",
    },
    {
        "id": "lapin",
        "name": "Sautin",
        "color": (0.95, 0.9, 0.85),
        "features": ["ears_long", "tail_puff"],
        "tagline": "Bondissant, toujours en train de jouer",
    },
    {
        "id": "ours",
        "name": "Doudou",
        "color": (0.6, 0.45, 0.35),
        "features": ["ears_round", "belly_round"],
        "tagline": "Costaud, doux, protecteur",
    },
    {
        "id": "robot",
        "name": "Byto",
        "color": (0.7, 0.75, 0.8),
        "features": ["antenna_robot", "panel_lines"],
        "tagline": "Précis, discipliné, fidèle",
    },
    {
        "id": "fantome",
        "name": "Vaporo",
        "color": (0.85, 0.85, 0.95),
        "features": ["wavy_bottom", "translucent"],
        "tagline": "Mystérieux, léger, flotte doucement",
    },
    {
        "id": "plante",
        "name": "Bourgeon",
        "color": (0.5, 0.8, 0.4),
        "features": ["leaves", "flower_head"],
        "tagline": "Paisible, grandit à sa façon",
    },
]


def get_species(species_id):
    for s in SPECIES:
        if s["id"] == species_id:
            return s
    return SPECIES[0]
