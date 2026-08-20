"""
main.py
Anima AI / Chrono-Fauna — app Kivy v2.

Ajouts : écran de sélection de créature (10 espèces à silhouettes
distinctes), état œuf, rythme réaliste (heures/jours via creature.py),
propreté (caca + douche), mort si négligée, redémarrage complet,
apprentissage de mots, notifications de rappel.
"""

import random
import math

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty

from creature import Creature
from ai_behavior import BehaviorAI
from sensors import SensorManager
from lifecycle import LifecycleManager
from species import SPECIES, get_species
import haptics
import notifications


# =================================================================
# Particules de feedback
# =================================================================
class Particle:
    def __init__(self, x, y, kind="heart"):
        self.x = x
        self.y = y
        self.kind = kind
        self.age = 0.0
        self.lifetime = 1.2
        self.vx = random.uniform(-20, 20)
        self.vy = random.uniform(40, 70)
        self.alpha = 1.0
        self.size = random.uniform(14, 22)

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy -= 20 * dt
        self.alpha = max(0.0, 1.0 - (self.age / self.lifetime))
        return self.age < self.lifetime


# =================================================================
# Widget de rendu de la créature (blob + silhouette selon l'espèce)
# =================================================================
class CreatureWidget(Widget):
    eye_scale = NumericProperty(1.0)
    breath_scale = NumericProperty(1.0)
    bg_color = ListProperty([0.05, 0.05, 0.12])

    def __init__(self, creature, behavior, **kwargs):
        super().__init__(**kwargs)
        self.creature = creature
        self.behavior = behavior
        self.particles = []
        self.species = get_species(creature.species_id)

        with self.canvas.before:
            self._bg_color = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle()

        with self.canvas:
            self.shadow_color = Color(0, 0, 0, 0.35)
            self.shadow = Ellipse()

            self.body_layers = []
            for i in range(4):
                c = Color(0, 0, 0, 0)
                e = Ellipse()
                self.body_layers.append((c, e))

            # Silhouette : jusqu'à 4 formes additionnelles selon l'espèce
            self.feature_color = Color(0, 0, 0, 1)
            self.feature_shapes = [Ellipse() for _ in range(6)]

            self.cheek_color = Color(1, 0.55, 0.6, 0.0)
            self.left_cheek = Ellipse()
            self.right_cheek = Ellipse()

            self.eye_color = Color(0.08, 0.08, 0.12)
            self.left_eye = Ellipse()
            self.right_eye = Ellipse()
            self.eye_glint_color = Color(1, 1, 1, 0.85)
            self.left_glint = Ellipse()
            self.right_glint = Ellipse()

            self.mouth_color = Color(0.15, 0.1, 0.12)
            self.mouth = Line(width=2.2)

            # Caca (petites formes marron si non nettoyé)
            self.poop_color = Color(0.4, 0.28, 0.15, 0)
            self.poop_shapes = [Ellipse() for _ in range(3)]

            self.particle_color = Color(1, 1, 1, 1)
            self.particle_shapes = []

        self.bind(pos=self.update_shapes, size=self.update_shapes)
        self.bind(eye_scale=self.update_shapes, breath_scale=self.update_shapes)
        self.bind(bg_color=self._sync_bg_color)

        Clock.schedule_interval(self.update_shapes, 1 / 30)
        Clock.schedule_interval(self.animate_blink, 3.5)
        self._start_breathing()

    def _sync_bg_color(self, *args):
        self._bg_color.rgba = (*self.bg_color, 1)

    def set_ambient(self, lux):
        night = (0.04, 0.04, 0.12)
        day = (0.55, 0.75, 0.95)
        r = night[0] + (day[0] - night[0]) * lux
        g = night[1] + (day[1] - night[1]) * lux
        b = night[2] + (day[2] - night[2]) * lux
        Animation(bg_color=[r, g, b], duration=2.0).start(self)

    def _start_breathing(self):
        anim = (
            Animation(breath_scale=1.04, duration=1.6, t="in_out_sine")
            + Animation(breath_scale=1.0, duration=1.6, t="in_out_sine")
        )
        anim.repeat = True
        anim.start(self)

    def animate_blink(self, dt):
        if self.creature.is_egg:
            return
        anim = (
            Animation(eye_scale=0.05, duration=0.06)
            + Animation(eye_scale=1.0, duration=0.09)
        )
        anim.start(self)

    def spawn_particles(self, kind, count=6):
        cx, cy = self.center
        for _ in range(count):
            px = cx + random.uniform(-40, 40)
            py = cy + random.uniform(-10, 30)
            self.particles.append(Particle(px, py, kind))
        while len(self.particle_shapes) < len(self.particles):
            with self.canvas:
                shape = Ellipse()
            self.particle_shapes.append(shape)

    def stage_scale(self):
        if self.creature.is_egg:
            return 0.55
        idx = self.creature.stage_index
        return min(0.65 + idx * 0.08, 1.15)

    def mood_bounce_offset(self):
        mood = self.behavior.current_mood
        t = Clock.get_boottime()
        if mood == "playful":
            return abs(math.sin(t * 6)) * 14
        if mood == "scared":
            return math.sin(t * 30) * 4
        if mood == "egg":
            return math.sin(t * 2) * 3
        return 0

    def update_shapes(self, *args):
        cx, cy = self.center
        scale = self.stage_scale() * self.breath_scale
        base_size = min(self.width, self.height) * 0.32 * scale
        bounce = self.mood_bounce_offset()

        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

        body_cx = cx
        body_cy = cy + bounce

        self.shadow_color.rgba = (0, 0, 0, 0.30)
        shadow_w = base_size * 1.5
        shadow_h = base_size * 0.35
        self.shadow.size = (shadow_w, shadow_h)
        self.shadow.pos = (cx - shadow_w / 2, cy - base_size * 0.75)

        base_r, base_g, base_b = self.creature.color

        if self.creature.is_egg:
            self._draw_egg(body_cx, body_cy, base_size, base_r, base_g, base_b)
            self._hide_features()
        else:
            for i, (color, ellipse) in enumerate(self.body_layers):
                t = i / (len(self.body_layers) - 1)
                shade = 1.0 - 0.28 * (1 - t)
                color.rgba = (base_r * shade, base_g * shade, base_b * shade, 1)
                w = base_size * 1.4 * (1 - t * 0.18)
                h = base_size * 1.2 * (1 - t * 0.18)
                offset_x = -base_size * 0.10 * t
                offset_y = base_size * 0.08 * t
                ellipse.size = (w, h)
                ellipse.pos = (body_cx - w / 2 + offset_x, body_cy - h / 2 + offset_y)

            self._draw_features(body_cx, body_cy, base_size, base_r, base_g, base_b)
            self._draw_face(body_cx, body_cy, base_size)

        self._draw_poop(cx, cy, base_size)

        while len(self.particle_shapes) < len(self.particles):
            with self.canvas:
                shape = Ellipse()
            self.particle_shapes.append(shape)
        for i, p in enumerate(self.particles):
            shape = self.particle_shapes[i]
            shape.pos = (p.x - p.size / 2, p.y - p.size / 2)
            shape.size = (p.size, p.size)

    def _hide_features(self):
        for shape in self.feature_shapes:
            shape.pos = (-1000, -1000)
        self.left_eye.pos = (-1000, -1000)
        self.right_eye.pos = (-1000, -1000)
        self.left_cheek.pos = (-1000, -1000)
        self.right_cheek.pos = (-1000, -1000)
        self.mouth.points = []

    def _draw_egg(self, cx, cy, size, r, g, b):
        for i, (color, ellipse) in enumerate(self.body_layers):
            t = i / (len(self.body_layers) - 1)
            shade = 1.0 - 0.2 * (1 - t)
            color.rgba = (min(1, r * shade + 0.3), min(1, g * shade + 0.3), min(1, b * shade + 0.3), 1)
            w = size * 1.1 * (1 - t * 0.15)
            h = size * 1.5 * (1 - t * 0.15)
            ellipse.size = (w, h)
            ellipse.pos = (cx - w / 2, cy - h / 2)
        # petites fissures simples via une ligne si proche de l'éclosion
        eye_h = 0
        self.left_eye.pos = (-1000, -1000)
        self.right_eye.pos = (-1000, -1000)

    def _draw_features(self, cx, cy, size, r, g, b):
        feats = self.species["features"]
        self.feature_color.rgba = (r * 0.7, g * 0.7, b * 0.7, 1)
        shapes = self.feature_shapes
        for s in shapes:
            s.pos = (-1000, -1000)

        i = 0
        if "ears_cat" in feats or "ears_round" in feats or "ears_long" in feats:
            ear_h = size * (0.5 if "ears_long" in feats else 0.28)
            ear_w = size * 0.16
            shapes[0].size = (ear_w, ear_h)
            shapes[0].pos = (cx - size * 0.45, cy + size * 0.35)
            shapes[1].size = (ear_w, ear_h)
            shapes[1].pos = (cx + size * 0.29, cy + size * 0.35)
            i = 2
        if "wings" in feats or "wings_small" in feats:
            wing_w = size * (0.55 if "wings" in feats else 0.32)
            wing_h = size * 0.32
            shapes[2].size = (wing_w, wing_h)
            shapes[2].pos = (cx - size * 0.95, cy - size * 0.05)
            shapes[3].size = (wing_w, wing_h)
            shapes[3].pos = (cx + size * 0.4, cy - size * 0.05)
        if "horns" in feats:
            shapes[4].size = (size * 0.1, size * 0.22)
            shapes[4].pos = (cx - size * 0.2, cy + size * 0.5)
            shapes[5].size = (size * 0.1, size * 0.22)
            shapes[5].pos = (cx + size * 0.1, cy + size * 0.5)
        if "antenna" in feats or "antenna_robot" in feats:
            shapes[4].size = (size * 0.06, size * 0.3)
            shapes[4].pos = (cx - size * 0.02, cy + size * 0.5)
        if "beak" in feats:
            shapes[4].size = (size * 0.18, size * 0.12)
            shapes[4].pos = (cx - size * 0.09, cy - size * 0.02)
        if "fins" in feats:
            shapes[2].size = (size * 0.3, size * 0.4)
            shapes[2].pos = (cx - size * 0.85, cy)
            shapes[3].size = (size * 0.3, size * 0.4)
            shapes[3].pos = (cx + size * 0.55, cy)
        if "leaves" in feats or "flower_head" in feats:
            shapes[4].size = (size * 0.3, size * 0.14)
            shapes[4].pos = (cx - size * 0.15, cy + size * 0.48)
            shapes[5].size = (size * 0.18, size * 0.18)
            shapes[5].pos = (cx - size * 0.09, cy + size * 0.55)

    def _draw_face(self, cx, cy, size):
        cheek_alpha = max(0.0, (self.creature.affection - 55) / 45) * 0.5
        self.cheek_color.a = cheek_alpha
        cheek_size = size * 0.28
        cheek_y = cy - size * 0.05
        self.left_cheek.size = (cheek_size, cheek_size * 0.7)
        self.left_cheek.pos = (cx - size * 0.62, cheek_y - cheek_size * 0.35)
        self.right_cheek.size = (cheek_size, cheek_size * 0.7)
        self.right_cheek.pos = (cx + size * 0.34, cheek_y - cheek_size * 0.35)

        eye_w = size * 0.16
        eye_h = eye_w * max(0.05, self.eye_scale)
        eye_y = cy + size * 0.12 - eye_h / 2
        lx = cx - size * 0.32
        rx = cx + size * 0.14
        self.left_eye.size = (eye_w, eye_h)
        self.left_eye.pos = (lx, eye_y)
        self.right_eye.size = (eye_w, eye_h)
        self.right_eye.pos = (rx, eye_y)

        glint_w = eye_w * 0.35
        self.left_glint.size = (glint_w, glint_w)
        self.left_glint.pos = (lx + eye_w * 0.15, eye_y + max(eye_h - glint_w * 0.6, 0))
        self.right_glint.size = (glint_w, glint_w)
        self.right_glint.pos = (rx + eye_w * 0.15, eye_y + max(eye_h - glint_w * 0.6, 0))

        mouth_cx = cx
        mouth_cy = cy - size * 0.18
        mood = self.behavior.current_mood
        w = size * 0.22
        if mood in ("affectionate", "playful"):
            points = []
            for i in range(11):
                a = math.pi * (i / 10)
                px = mouth_cx - w + (2 * w) * (i / 10)
                py = mouth_cy - math.sin(a) * size * 0.09
                points += [px, py]
            self.mouth.points = points
        elif mood == "hungry":
            points = []
            for i in range(21):
                a = 2 * math.pi * (i / 20)
                px = mouth_cx + math.cos(a) * size * 0.07
                py = mouth_cy + math.sin(a) * size * 0.07
                points += [px, py]
            self.mouth.points = points
        elif mood == "scared":
            points = []
            for i in range(7):
                px = mouth_cx - w * 0.6 + (1.2 * w) * (i / 6)
                py = mouth_cy + (size * 0.03 if i % 2 == 0 else -size * 0.03)
                points += [px, py]
            self.mouth.points = points
        elif mood in ("tired", "dirty"):
            self.mouth.points = [
                mouth_cx - w * 0.7, mouth_cy,
                mouth_cx, mouth_cy - size * 0.02,
                mouth_cx + w * 0.7, mouth_cy,
            ]
        else:
            self.mouth.points = [mouth_cx - w * 0.6, mouth_cy, mouth_cx + w * 0.6, mouth_cy]

    def _draw_poop(self, cx, cy, size):
        count = min(self.creature.poop_count, 3)
        self.poop_color.a = 1.0 if count > 0 else 0.0
        for i, shape in enumerate(self.poop_shapes):
            if i < count:
                shape.size = (size * 0.18, size * 0.14)
                shape.pos = (cx - size * 0.9 + i * size * 0.35, cy - size * 0.9)
            else:
                shape.pos = (-1000, -1000)


# =================================================================
# Écran de sélection de créature
# =================================================================
class SelectionScreen(Screen):
    def __init__(self, on_select, **kwargs):
        super().__init__(**kwargs)
        self.on_select = on_select

        root = BoxLayout(orientation="vertical")
        title = Label(
            text="Choisis ton compagnon",
            size_hint=(1, 0.12),
            font_size="22sp",
            bold=True,
        )
        root.add_widget(title)

        scroll = ScrollView(size_hint=(1, 0.88))
        grid = GridLayout(cols=2, spacing=10, padding=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for sp in SPECIES:
            card = self._build_card(sp)
            grid.add_widget(card)

        scroll.add_widget(grid)
        root.add_widget(scroll)
        self.add_widget(root)

    def _build_card(self, sp):
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=180, padding=6, spacing=4)

        preview = Widget(size_hint=(1, 0.6))
        with preview.canvas:
            r, g, b = sp["color"]
            Color(r, g, b, 1)
            circle = Ellipse(size=(70, 70))

        def position_circle(instance, value):
            circle.pos = (
                instance.center_x - 35,
                instance.center_y - 35,
            )
        preview.bind(pos=position_circle, size=position_circle)

        name_label = Label(text=sp["name"], font_size="16sp", bold=True, size_hint=(1, 0.2))
        tagline_label = Label(
            text=sp["tagline"], font_size="11sp", size_hint=(1, 0.2), color=(0.8, 0.8, 0.8, 1)
        )

        box.add_widget(preview)
        box.add_widget(name_label)
        box.add_widget(tagline_label)

        btn = Button(text="Choisir", size_hint=(1, None), height=36)
        btn.bind(on_release=lambda inst, s=sp: self.on_select(s["id"]))
        box.add_widget(btn)

        return box


# =================================================================
# Écran de jeu principal
# =================================================================
class GameScreen(Screen):
    def __init__(self, creature, on_death, **kwargs):
        super().__init__(**kwargs)
        self.creature = creature
        self.behavior = BehaviorAI(creature)
        self.lifecycle = LifecycleManager(creature)
        self.sensors = SensorManager()
        self.sensors.start_light_sensor()
        self.on_death = on_death

        root = BoxLayout(orientation="vertical")

        self.creature_widget = CreatureWidget(creature, self.behavior, size_hint=(1, 0.5))
        root.add_widget(self.creature_widget)

        self.status_label = Label(text="", size_hint=(1, 0.13), font_size="14sp")
        root.add_widget(self.status_label)

        self.word_input = TextInput(
            hint_text="Apprends-lui un mot...",
            multiline=False,
            size_hint=(1, 0.08),
        )
        self.word_input.bind(on_text_validate=self.on_teach_word)
        root.add_widget(self.word_input)

        button_row = BoxLayout(size_hint=(1, 0.15), spacing=5, padding=5)
        for label, callback in [
            ("Nourrir", self.on_feed),
            ("Jouer", self.on_play),
            ("Caresser", self.on_pet),
            ("Reposer", self.on_rest),
            ("Nettoyer", self.on_clean),
        ]:
            btn = Button(text=label, font_size="12sp")
            btn.bind(on_release=callback)
            button_row.add_widget(btn)
        root.add_widget(button_row)

        self.add_widget(root)

        Clock.schedule_interval(self.game_tick, 1.0)
        Clock.schedule_interval(self.particle_tick, 1 / 30)

    def game_tick(self, dt):
        self.creature.tick()
        self.behavior.evaluate()

        lux = self.sensors.read_light_level()
        self.behavior.reaction_to_light(lux)
        self.creature_widget.set_ambient(lux)

        events = self.lifecycle.poll_events()
        for name, data in events:
            if name == "hatched":
                self.status_label.text = f"{self.creature.name} vient d'éclore !"
                haptics.pulse(0.2)
            elif name == "evolved":
                self.status_label.text = f"{self.creature.name} a évolué !"
                haptics.pulse(0.2)
            elif name == "died":
                self.status_label.text = f"{self.creature.name} n'a pas survécu..."
                Creature.delete_save()
                Clock.schedule_once(lambda dtt: self.on_death(), 2.5)

        if self.creature.alive and events == []:
            mood = self.behavior.current_mood
            if self.creature.is_egg:
                remaining_h = max(0, (self.creature.birth_time + 1.5 * 86400 - __import__("time").time()) / 3600)
                self.status_label.text = f"Un œuf... encore ~{remaining_h:.1f}h avant l'éclosion"
            else:
                vocab_txt = f" | Mots: {len(self.creature.vocabulary)}" if self.creature.vocabulary else ""
                self.status_label.text = (
                    f"{self.creature.name} — {self.creature.stage_name()} — {mood}\n"
                    f"Faim: {int(self.creature.hunger)}  Énergie: {int(self.creature.energy)}  "
                    f"Affection: {int(self.creature.affection)}  Propreté: {int(self.creature.cleanliness)}"
                    f"{vocab_txt}"
                )

        notifications.check_and_notify(self.creature)
        self.creature.save()

    def particle_tick(self, dt):
        cw = self.creature_widget
        cw.particles = [p for p in cw.particles if p.update(dt)]
        for i, p in enumerate(cw.particles):
            if i < len(cw.particle_shapes):
                shape = cw.particle_shapes[i]
                shape.pos = (p.x - p.size / 2, p.y - p.size / 2)
                shape.size = (p.size, p.size)
        for i in range(len(cw.particles), len(cw.particle_shapes)):
            cw.particle_shapes[i].pos = (-1000, -1000)

    def on_feed(self, instance):
        if self.creature.feed():
            haptics.pulse(0.08)
            self.creature_widget.spawn_particles("crumb", count=5)

    def on_play(self, instance):
        if self.creature.play():
            haptics.purr_pattern()
            self.creature_widget.spawn_particles("spark", count=6)
        else:
            self.status_label.text = f"{self.creature.name} a assez joué pour aujourd'hui."

    def on_pet(self, instance):
        if self.creature.pet():
            haptics.heartbeat_pattern()
            self.creature_widget.spawn_particles("heart", count=5)

    def on_rest(self, instance):
        self.creature.rest()

    def on_clean(self, instance):
        if self.creature.clean():
            haptics.pulse(0.1)

    def on_teach_word(self, instance):
        word = self.word_input.text
        if self.creature.teach_word(word):
            self.status_label.text = f"{self.creature.name} a appris le mot \"{word}\" !"
        self.word_input.text = ""


# =================================================================
# App
# =================================================================
class AnimaAIApp(App):
    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())
        existing = Creature.load()
        if existing is not None and existing.alive:
            self._start_game(existing)
        else:
            self._show_selection()
        return self.sm

    def _show_selection(self):
        if self.sm.has_screen("selection"):
            self.sm.remove_widget(self.sm.get_screen("selection"))
        screen = SelectionScreen(on_select=self._on_species_chosen, name="selection")
        self.sm.add_widget(screen)
        self.sm.current = "selection"

    def _on_species_chosen(self, species_id):
        creature = Creature(species_id=species_id, name=get_species(species_id)["name"])
        creature.save()
        self._start_game(creature)

    def _start_game(self, creature):
        if self.sm.has_screen("game"):
            self.sm.remove_widget(self.sm.get_screen("game"))
        screen = GameScreen(creature, on_death=self._show_selection, name="game")
        self.sm.add_widget(screen)
        self.sm.current = "game"

    def on_stop(self):
        if self.sm.current == "game":
            self.sm.get_screen("game").creature.save()


if __name__ == "__main__":
    AnimaAIApp().run()
