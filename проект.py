import pygame
from PIL import Image
import math
import random
from collections import deque

def extract_gif_frames(gif_path):
    frames = []
    with Image.open(gif_path) as gif:
        for i in range(gif.n_frames):
            gif.seek(i)
            frame = gif.copy().convert("RGBA")
            frames.append(frame)
    return frames

def load_frames_as_surfaces(pil_frames):
    surfaces = []
    for frame in pil_frames:
        surface = pygame.Surface(frame.size, pygame.SRCALPHA)
        surface.blit(pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode), (0, 0))
        surfaces.append(surface)
    return surfaces

def make_circular_surface(image):
    size = image.get_size()
    mask = pygame.Surface(size, pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    center = (size[0] // 2, size[1] // 2)
    radius = min(size) // 2
    pygame.draw.circle(mask, (255, 255, 255, 255), center, radius)
    circular = pygame.Surface(size, pygame.SRCALPHA)
    circular.blit(image, (0, 0))
    circular.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
    return circular

pygame.init()

WIDTH, HEIGHT = 1400, 830
tekushaya_shirina, tekushaya_vysota = WIDTH, HEIGHT
screen = pygame.display.set_mode((tekushaya_shirina, tekushaya_vysota), pygame.RESIZABLE)
pygame.display.set_caption("Космический симулятор")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 150, 255)
LIGHT_BLUE = (150, 200, 255)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 0)
RED = (255, 100, 100)
ORANGE = (255, 165, 0)
PURPLE = (200, 100, 255)
POLZUNOK_CVET = (100, 100, 255)
POLZUNOK_RUCHKA_CVET = (200, 200, 255)

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 72)

background_original = pygame.image.load('космос.jpg').convert()

class Notification:
    def __init__(self, text, duration=3.0):
        self.text = text
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.alpha = 255
        self.y_offset = 0

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = small_font.render(test_line, True, YELLOW)

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def update(self):
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        if elapsed > self.duration:
            return False
        if elapsed > self.duration - 0.5:
            self.alpha = int(255 * (1 - (elapsed - (self.duration - 0.5)) / 0.5))
        return True

    def draw(self, screen, screen_width, y_position):
        max_text_width = min(screen_width - 100, 500)

        lines = self.wrap_text(self.text, max_text_width)

        text_surfaces = []
        total_height = 0
        for line in lines:
            text_surf = small_font.render(line, True, YELLOW)
            text_surf.set_alpha(self.alpha)
            text_surfaces.append(text_surf)
            total_height += text_surf.get_height()

        total_height += (len(lines) - 1) * 3

        max_line_width = max([surf.get_width() for surf in text_surfaces]) if text_surfaces else 0
        bg_rect = pygame.Rect(0, 0, max_line_width + 40, total_height + 20)
        bg_rect.centerx = screen_width // 2
        bg_rect.y = y_position

        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, int(180 * self.alpha / 255)))
        pygame.draw.rect(bg_surf, (50, 50, 50, int(180 * self.alpha / 255)), bg_surf.get_rect(), border_radius=8)
        pygame.draw.rect(bg_surf, YELLOW, bg_surf.get_rect(), 1, border_radius=8)
        screen.blit(bg_surf, bg_rect)

        current_y = bg_rect.y + 10
        for text_surf in text_surfaces:
            text_rect = text_surf.get_rect(centerx=bg_rect.centerx, y=current_y)
            screen.blit(text_surf, text_rect)
            current_y += text_surf.get_height() + 3

class NotificationManager:
    def __init__(self, max_notifications=3):
        self.notifications = deque()
        self.max_notifications = max_notifications
        self.notification_height = 80
        self.spacing = 10

    def add(self, text, duration=3.0):
        self.notifications.append(Notification(text, duration))
        if len(self.notifications) > self.max_notifications:
            self.notifications.popleft()

    def update(self):
        self.notifications = [n for n in self.notifications if n.update()]

    def draw(self, screen, screen_width):
        y_offset = 80
        for i, notification in enumerate(self.notifications):
            notification.draw(screen, screen_width, y_offset + i * (self.notification_height + self.spacing))

    def clear(self):
        self.notifications.clear()

class ControllableBackground:
    def __init__(self, image):
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()
        self.camera_x = 0
        self.camera_y = 0
        self.dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.scroll_speed = 1.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if not self._is_click_on_ui(mouse_pos):
                    self.dragging = True
                    self.last_mouse_x = event.pos[0]
                    self.last_mouse_y = event.pos[1]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                dx = event.pos[0] - self.last_mouse_x
                dy = event.pos[1] - self.last_mouse_y
                self.camera_x -= dx * self.scroll_speed
                self.camera_y -= dy * self.scroll_speed
                self.last_mouse_x = event.pos[0]
                self.last_mouse_y = event.pos[1]

    def _is_click_on_ui(self, pos):
        menu_y = 10
        menu_width = 60
        menu_height = 30
        main_rects = [
            pygame.Rect(10, menu_y, menu_width, menu_height),
            pygame.Rect(10 + menu_width + 10, menu_y, menu_width, menu_height),
            pygame.Rect(10 + 2*(menu_width + 10), menu_y, menu_width, menu_height)
        ]
        for rect in main_rects:
            if rect.collidepoint(pos):
                return True

        knopka_start = pygame.Rect(tekushaya_shirina // 2 - 50, tekushaya_vysota - 150, 100, 50)
        if knopka_start.collidepoint(pos):
            return True

        knopka_menu = pygame.Rect(tekushaya_shirina - 110, 22, 100, 36)
        if knopka_menu.collidepoint(pos):
            return True

        knopka_shirina, knopka_vysota = 100, 50
        plyus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 - knopka_shirina - 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)
        minus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 + 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)
        if plyus_pryamougolnik.collidepoint(pos) or minus_pryamougolnik.collidepoint(pos):
            return True

        if hasattr(self, 'polzunok') and self.polzunok.rucka_pryamougolnik().collidepoint(pos):
            return True

        return False

    def draw(self, screen, screen_width, screen_height):
        start_x = int(self.camera_x) % self.width - self.width
        start_y = int(self.camera_y) % self.height - self.height

        for x in range(start_x, screen_width + self.width, self.width):
            for y in range(start_y, screen_height + self.height, self.height):
                screen.blit(self.image, (x, y))

    def world_to_screen(self, world_x, world_y):
        screen_x = world_x + self.camera_x
        screen_y = world_y + self.camera_y
        return screen_x, screen_y

    def set_polzunok(self, polzunok):
        self.polzunok = polzunok

controllable_bg = ControllableBackground(background_original)

GIF_PATH = "sun.gif"
pil_frames = extract_gif_frames(GIF_PATH)
gif_frames = load_frames_as_surfaces(pil_frames)
solnce_original_razmer = gif_frames[0].get_width()

SCALE_FACTOR = 0.4
masshtabirovannye_kadry = []
for frame in gif_frames:
    masshtabirovannaya_poverhnost = pygame.transform.smoothscale(frame, (int(frame.get_width() * SCALE_FACTOR), int(frame.get_height() * SCALE_FACTOR)))
    masshtabirovannye_kadry.append(masshtabirovannaya_poverhnost)

knopka_shirina, knopka_vysota = 100, 50
knopka_cvet = (50, 50, 50)
knopka_navedenie_cvet = (100, 100, 100)

tekushiy_kadr = 0
zaderzhka_kadra = 100
poslednee_obnovlenie = pygame.time.get_ticks()

planeta_ikona = pygame.image.load('значок_планеты.jpg').convert_alpha()
planeta_ikona = pygame.transform.scale(planeta_ikona, (67, 50))
zvezda_ikona = pygame.image.load('значок_звезды.webp').convert_alpha()
zvezda_ikona = pygame.transform.scale(zvezda_ikona, (74, 50))
asteroid_ikona = pygame.image.load('значок_астероида.webp').convert_alpha()
asteroid_ikona = pygame.transform.scale(asteroid_ikona, (67, 50))

class PolzunokSkorosti:
    def __init__(self, x, y, width, height):
        self.pryamougolnik = pygame.Rect(x, y, width, height)
        self.max_skorost = 1000
        self.min_skorost = 0
        self.skorost = 440
        self.ruchka_x = x + (self.skorost / self.max_skorost) * width
        self.ruchka_shirina = 20
        self.ruchka_vysota = height + 10
        self.peretaskivaetsya = False

    def rucka_pryamougolnik(self):
        return pygame.Rect(self.ruchka_x - self.ruchka_shirina // 2,
                          self.pryamougolnik.y - 5,
                          self.ruchka_shirina,
                          self.ruchka_vysota)

    def obnovit(self, mouse_pos, mouse_pressed):
        rucka_rect = self.rucka_pryamougolnik()

        if mouse_pressed[0]:
            if rucka_rect.collidepoint(mouse_pos) or self.peretaskivaetsya:
                self.peretaskivaetsya = True
                self.ruchka_x = max(self.pryamougolnik.left, min(mouse_pos[0], self.pryamougolnik.right))
                self.skorost = ((self.ruchka_x - self.pryamougolnik.left) / self.pryamougolnik.width) * (self.max_skorost - self.min_skorost) + self.min_skorost
        else:
            self.peretaskivaetsya = False

    def narisovat(self, screen):
        pygame.draw.rect(screen, GRAY, self.pryamougolnik, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.pryamougolnik, 2, border_radius=5)

        zapolnennaya_shirina = self.ruchka_x - self.pryamougolnik.left
        if zapolnennaya_shirina > 0:
            zapolnennyy_pryamougolnik = pygame.Rect(self.pryamougolnik.left, self.pryamougolnik.top, zapolnennaya_shirina, self.pryamougolnik.height)
            pygame.draw.rect(screen, POLZUNOK_CVET, zapolnennyy_pryamougolnik, border_radius=5)

        rucka_rect = self.rucka_pryamougolnik()
        pygame.draw.rect(screen, POLZUNOK_RUCHKA_CVET, rucka_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, rucka_rect, 2, border_radius=8)

        k = self.poluchit_koefficient_skorosti()
        skorost_text = small_font.render(f"Скорость: {k:.2f}x", True, YELLOW)
        text_rect = skorost_text.get_rect(midleft=(self.pryamougolnik.right + 10, self.pryamougolnik.centery))
        screen.blit(skorost_text, text_rect)

    def poluchit_koefficient_skorosti(self):
        return 0.1 + (self.skorost / 1000.0) * 0.9

def zagruzit_i_sdelat_kruglym(path, size):
    try:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (size, size))
        return make_circular_surface(image)
    except:
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((100, 100, 100))
        return make_circular_surface(surface)

koficzienty_razmera_zvezd = {
    "Sverhgiant": 1.4,
    "Gigant": 1.0,
    "Belyy_karlik": 0.8,
}

imena_zvezd = set(koficzienty_razmera_zvezd.keys())

nebesnye_obekty = {
    "zheleznaya_planeta": {"image": zagruzit_i_sdelat_kruglym('Железная планета.png', 120), "base_size": 120, "positions": [], "name_ru": "Железная планета", "description": "Планета с высоким содержанием железа. Очень плотная, имеет сильное магнитное поле. Масса измеряется в массах Земли."},
    "gazovaya_planeta": {"image": zagruzit_i_sdelat_kruglym('Газовая планета.png', 180), "base_size": 180, "positions": [], "name_ru": "Газовая планета", "description": "Состоит в основном из водорода и гелия. Имеет низкую плотность, но огромные размеры. Масса измеряется в массах Земли."},
    "ledyanaya_planeta": {"image": zagruzit_i_sdelat_kruglym('Ледяная планета.png', 140), "base_size": 140, "positions": [], "name_ru": "Ледяная планета", "description": "Планета, покрытая льдом и замерзшими газами. Обитаема для некоторых форм жизни. Масса измеряется в массах Земли."},
    "Sverhgiant": {"image": zagruzit_i_sdelat_kruglym('Сверхгигант.png', int(solnce_original_razmer * koficzienty_razmera_zvezd["Sverhgiant"] * 0.7)),
               "base_size": int(solnce_original_razmer * koficzienty_razmera_zvezd["Sverhgiant"] * 0.7), "positions": [], "name_ru": "Сверхгигант", "description": "Огромная звезда, в десятки раз больше Солнца. Живет всего несколько миллионов лет. Масса измеряется в массах Солнца."},
    "Gigant": {"image": zagruzit_i_sdelat_kruglym('Гигант.png', int(solnce_original_razmer * koficzienty_razmera_zvezd["Gigant"] * 0.7)),
                "base_size": int(solnce_original_razmer * koficzienty_razmera_zvezd["Gigant"] * 0.7), "positions": [], "name_ru": "Гигант", "description": "Звезда, которая расширилась после выгорания водорода в ядре. Масса измеряется в массах Солнца."},
    "Belyy_karlik": {"image": zagruzit_i_sdelat_kruglym('Белый карлик.png', int(solnce_original_razmer * koficzienty_razmera_zvezd["Belyy_karlik"] * 0.7)),
                 "base_size": int(solnce_original_razmer * koficzienty_razmera_zvezd["Belyy_karlik"] * 0.7), "positions": [], "name_ru": "Белый карлик", "description": "Остывшая звезда размером с Землю, но массой как Солнце. Очень плотная. Масса измеряется в массах Солнца."},
    "Metallicheskii": {"image": zagruzit_i_sdelat_kruglym('Металлический.png', 140), "base_size": 140, "positions": [], "name_ru": "Металлический астероид", "description": "Астероид, состоящий в основном из металлов (железа, никеля). Масса измеряется в массах Земли."},
    "Siikatnii": {"image": zagruzit_i_sdelat_kruglym('Силикатный.png', 140), "base_size": 140, "positions": [], "name_ru": "Силикатный астероид", "description": "Каменный астероид, состоящий из силикатов. Самый распространенный тип. Масса измеряется в массах Земли."},
    "Uglerodnii": {"image": zagruzit_i_sdelat_kruglym('Углеродный.png', 140), "base_size": 140, "positions": [], "name_ru": "Углеродный астероид", "description": "Астероид, богатый углеродом и органическими соединениями. Масса измеряется в массах Земли."},
}

class SunObject:
    def __init__(self):
        self.pos = [WIDTH//2, HEIGHT//2]
        self.mass = 5000
        self.radius = 50
        self.vx = 0
        self.vy = 0
        self.image = None
        self.name_ru = "Солнце"
        self.yavlyaetsya_zvezdoy = True
        self.is_alive = True
        self.original_pos = [WIDTH//2, HEIGHT//2]
        self.saved_pos = [WIDTH//2, HEIGHT//2]

sun = SunObject()

vybrannyy_obekt = None
tekushchee_menu = "main"
menus = {}

rezhim_vvoda = 0
vvedennyy_text = ""
zapros_massy = "Введите массу объекта (в массах Земли):"
tekushchiy_zapros = zapros_massy
ozhidaemyy_obekt = None
ozhidaemaya_massa = None

REZHIM_SBORKI = "sbor"
REZHIM_SIMULYATSII = "sim"
REZHIM_MENU = "menu"
tekushchiy_rezhim = REZHIM_MENU

knopka_start = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 150, 100, 50)
knopka_start_cvet = (0, 200, 0)
knopka_start_navedenie_cvet = (0, 255, 0)

vremennye_obekty = {}
notification_manager = NotificationManager(max_notifications=3)

def add_notification(text, duration=3.0):
    notification_manager.add(text, duration)
    print(f"Уведомление: {text}")

def sozdat_vremennye_obekty():
    global vremennye_obekty
    vremennye_obekty = {}
    for imya, dannye in nebesnye_obekty.items():
        vremennye_obekty[imya] = {
            "image": dannye["image"],
            "base_size": dannye["base_size"],
            "positions": [],
            "name_ru": dannye.get("name_ru", imya),
            "description": dannye.get("description", "")
        }

sozdat_vremennye_obekty()

def zapustit_simulyatsiyu():
    global tekushchiy_rezhim, nebesnye_obekty, vremennye_obekty, sun

    for imya in nebesnye_obekty:
        nebesnye_obekty[imya]["positions"] = []

    for imya, dannye in vremennye_obekty.items():
        for pozitsiya in dannye["positions"]:
            novyy_obekt = pozitsiya.copy()
            nebesnye_obekty[imya]["positions"].append(novyy_obekt)

    if sun.is_alive:
        sun.saved_pos = sun.pos.copy()

    sun.fixed = False
    tekushchiy_rezhim = REZHIM_SIMULYATSII
    add_notification("Симуляция запущена!", 2.0)

def vernutsya_v_sborku():
    global tekushchiy_rezhim, vremennye_obekty, sun

    for imya in vremennye_obekty:
        vremennye_obekty[imya]["positions"] = []

    for imya, dannye in nebesnye_obekty.items():
        for pozitsiya in dannye["positions"]:
            vremennye_obekty[imya]["positions"].append(pozitsiya.copy())

    if sun.is_alive:
        sun.vx = 0
        sun.vy = 0
        sun.fixed = False
        sun.saved_pos = sun.pos.copy()
        add_notification("Режим сборки активирован. Солнце осталось на своей позиции.", 2.0)
    else:
        add_notification("Режим сборки активирован, но Солнце мертво.", 2.0)

    tekushchiy_rezhim = REZHIM_SBORKI

def vernutsya_v_glavnoe_menu():
    global tekushchiy_rezhim, vremennye_obekty, sun, ozhidaemyy_obekt, ozhidaemaya_massa, rezhim_vvoda

    for imya in vremennye_obekty:
        vremennye_obekty[imya]["positions"] = []

    sun.is_alive = True
    sun.pos = sun.original_pos.copy()
    sun.saved_pos = sun.original_pos.copy()
    sun.vx = 0
    sun.vy = 0
    sun.mass = 5000

    ozhidaemyy_obekt = None
    ozhidaemaya_massa = None
    rezhim_vvoda = 0

    tekushchiy_rezhim = REZHIM_MENU
    notification_manager.clear()
    add_notification("Возврат в главное меню", 2.0)

def vybrat_obekt(imya_obekta):
    global rezhim_vvoda, ozhidaemyy_obekt, tekushchiy_zapros, vvedennyy_text
    if not sun.is_alive and tekushchiy_rezhim == REZHIM_SBORKI:
        add_notification("Солнце мертво! Вы можете размещать объекты, но гравитации не будет до запуска симуляции.", 2.0)
    ozhidaemyy_obekt = imya_obekta
    rezhim_vvoda = 1
    vvedennyy_text = ""
    if imya_obekta in imena_zvezd:
        tekushchiy_zapros = "Введите массу объекта (в массах Солнца):"
    else:
        tekushchiy_zapros = zapros_massy
    print(f"Выбран объект: {imya_obekta}")

def sozdat_menyu():
    global menus
    menus["main"] = [
        {"text": "Планеты", "submenu": "planets", "icon": planeta_ikona},
        {"text": "Звезды", "submenu": "stars", "icon": zvezda_ikona},
        {"text": "Астероиды", "submenu": "asteroid", "icon": asteroid_ikona},
    ]
    menus["planets"] = [
        {"text": "Железная планета", "action": lambda: vybrat_obekt("zheleznaya_planeta")},
        {"text": "Газовая планета", "action": lambda: vybrat_obekt("gazovaya_planeta")},
        {"text": "Ледяная планета", "action": lambda: vybrat_obekt("ledyanaya_planeta")},
    ]
    menus["stars"] = [
        {"text": "Сверхгигант", "action": lambda: vybrat_obekt("Sverhgiant")},
        {"text": "Гигант", "action": lambda: vybrat_obekt("Gigant")},
        {"text": "Белый карлик", "action": lambda: vybrat_obekt("Belyy_karlik")},
    ]
    menus["asteroid"] = [
        {"text": "Металлический", "action": lambda: vybrat_obekt("Metallicheskii")},
        {"text": "Силикатный", "action": lambda: vybrat_obekt("Siikatnii")},
        {"text": "Углеродный", "action": lambda: vybrat_obekt("Uglerodnii")},
    ]

sozdat_menyu()

def narisovat_text_ili_ikonu(item, rect, navedenie=False):
    if "icon" in item:
        icon_surf = item["icon"]
        if icon_surf == zvezda_ikona:
            bg_rect = rect.inflate(25, 20)
            pygame.draw.rect(screen, WHITE, bg_rect, border_radius=8)
        icon_rect = icon_surf.get_rect(center=rect.center)
        screen.blit(icon_surf, icon_rect)
    else:
        color = BLACK
        bg_color = LIGHT_BLUE if navedenie else WHITE
        if tekushchee_menu != "main":
            rect.width = 250
        pygame.draw.rect(screen, bg_color, rect, border_radius=4)
        text_surf = font.render(item["text"], True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

def obrabotat_nazhatie_menu(pos):
    global tekushchee_menu
    for item in menus[tekushchee_menu]:
        if "rect" in item and item["rect"] and item["rect"].collidepoint(pos):
            if "submenu" in item:
                tekushchee_menu = item["submenu"]
                return
            elif "action" in item:
                item["action"]()
                return
    if tekushchee_menu != "main":
        tekushchee_menu = "main"

def proverit_kolliziyu_s_obektami(pos, novyy_radius):
    if tekushchiy_rezhim == REZHIM_SBORKI:
        obekty = vremennye_obekty
    else:
        obekty = nebesnye_obekty

    if sun.is_alive:
        dx = pos[0] - sun.pos[0]
        dy = pos[1] - sun.pos[1]
        rasstoyanie_do_solnca = math.sqrt(dx*dx + dy*dy)
        solnechnyy_radius = sun.radius

        if rasstoyanie_do_solnca < (novyy_radius + solnechnyy_radius):
            return False, "Солнце"

    for imya_obekta, dannye_obekta in obekty.items():
        for razmeshchennyy_obekt in dannye_obekta["positions"]:
            dx = pos[0] - razmeshchennyy_obekt["pos"][0]
            dy = pos[1] - razmeshchennyy_obekt["pos"][1]
            rasstoyanie = math.sqrt(dx*dx + dy*dy)
            drugoy_radius = razmeshchennyy_obekt.get("radius", 20)

            if rasstoyanie < (novyy_radius + drugoy_radius + 50):
                return False, dannye_obekta.get("name_ru", imya_obekta)

    return True, None

def vychislit_orbitalnuyu_skorost(massa_centra, rasstoyanie):
    G_grav = 200
    return math.sqrt(G_grav * massa_centra / rasstoyanie)

def nayti_dominiruyuschiy_gravitacionnyy_centr(poziciya):
    if tekushchiy_rezhim == REZHIM_SBORKI:
        obekty = vremennye_obekty
    else:
        obekty = nebesnye_obekty

    vse_zvezdy = []

    if sun.is_alive:
        vse_zvezdy.append({
            "mass": sun.mass,
            "pos": (sun.pos[0], sun.pos[1]),
            "name_ru": "Солнце"
        })

    for imya_obekta, dannye_obekta in obekty.items():
        if imya_obekta in imena_zvezd:
            for zvezda in dannye_obekta["positions"]:
                vse_zvezdy.append({
                    "mass": zvezda["mass"],
                    "pos": (zvezda["pos"][0], zvezda["pos"][1]),
                    "name_ru": dannye_obekta.get("name_ru", imya_obekta)
                })

    if not vse_zvezdy:
        return None

    max_vliyanie = 0
    dominant_center = vse_zvezdy[0]

    for zvezda in vse_zvezdy:
        dx = poziciya[0] - zvezda["pos"][0]
        dy = poziciya[1] - zvezda["pos"][1]
        r2 = dx*dx + dy*dy
        if r2 > 0:
            vliyanie = zvezda["mass"] / r2
            if vliyanie > max_vliyanie:
                max_vliyanie = vliyanie
                dominant_center = zvezda

    return dominant_center

def razmestit_obekt_s_massoy(pos, imya_obekta, massa, rezhim=REZHIM_SBORKI):
    try:
        znachenie_massy = float(massa)
        znachenie_massy = max(0.1, min(znachenie_massy, 100))

        yavlyaetsya_zvezdoy = imya_obekta in imena_zvezd

        if yavlyaetsya_zvezdoy:
            mnozhitel_razmera = 1.0 + (znachenie_massy ** 0.5) * 0.5
        else:
            mnozhitel_razmera = 0.8 + (znachenie_massy ** 0.5) / 8

        dannye_obekta = nebesnye_obekty[imya_obekta]
        bazovyy_razmer = dannye_obekta["base_size"]
        novyy_razmer = int(bazovyy_razmer * mnozhitel_razmera * SCALE_FACTOR)
        novyy_radius = novyy_razmer // 2

        world_x = pos[0] - controllable_bg.camera_x
        world_y = pos[1] - controllable_bg.camera_y

        mozhno_razmestit, imya_kollidiruyuschego = proverit_kolliziyu_s_obektami((world_x, world_y), novyy_radius)

        if not mozhno_razmestit:
            add_notification(f"Невозможно разместить! Слишком близко к {imya_kollidiruyuschego}", 2.0)
            return False

        originalnoe_izobrazhenie = dannye_obekta["image"]
        masshtabirovannoe_izobrazhenie = pygame.transform.smoothscale(originalnoe_izobrazhenie, (novyy_razmer, novyy_razmer))

        if masshtabirovannoe_izobrazhenie.get_width() != masshtabirovannoe_izobrazhenie.get_height():
            size = max(masshtabirovannoe_izobrazhenie.get_width(), masshtabirovannoe_izobrazhenie.get_height())
            square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            square_surface.fill((0, 0, 0, 0))
            x_offset = (size - masshtabirovannoe_izobrazhenie.get_width()) // 2
            y_offset = (size - masshtabirovannoe_izobrazhenie.get_height()) // 2
            square_surface.blit(masshtabirovannoe_izobrazhenie, (x_offset, y_offset))
            masshtabirovannoe_izobrazhenie = make_circular_surface(square_surface)
        else:
            masshtabirovannoe_izobrazhenie = make_circular_surface(masshtabirovannoe_izobrazhenie)

        dominant_center = nayti_dominiruyuschiy_gravitacionnyy_centr((world_x, world_y))

        if dominant_center and not yavlyaetsya_zvezdoy:
            dx = world_x - dominant_center["pos"][0]
            dy = world_y - dominant_center["pos"][1]
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                orbital_speed = vychislit_orbitalnuyu_skorost(dominant_center["mass"], distance)

                perp_x = -dy / distance
                perp_y = dx / distance
                direction = random.choice([-1, 1])

                vx = perp_x * orbital_speed * direction
                vy = perp_y * orbital_speed * direction
            else:
                vx, vy = 0, 0
        else:
            vx, vy = 0, 0

        novyy_obekt = {
            "pos": [world_x, world_y],
            "image": masshtabirovannoe_izobrazhenie,
            "mass": znachenie_massy * (1000 if yavlyaetsya_zvezdoy else 10),
            "original_size": bazovyy_razmer,
            "size_multiplier": mnozhitel_razmera,
            "yavlyaetsya_zvezdoy": yavlyaetsya_zvezdoy,
            "radius": novyy_razmer // 2,
            "vx": vx,
            "vy": vy,
            "name_ru": dannye_obekta.get("name_ru", imya_obekta),
            "mass_value": znachenie_massy
        }

        if rezhim == REZHIM_SBORKI:
            vremennye_obekty[imya_obekta]["positions"].append(novyy_obekt)
            print(f"Объект {imya_obekta} добавлен на позицию {world_x}, {world_y} с массой {znachenie_massy}")
            if dominant_center and not yavlyaetsya_zvezdoy:
                add_notification(f"Объект размещен на орбите вокруг {dominant_center.get('name_ru', 'звезды')}", 2.0)
        else:
            nebesnye_obekty[imya_obekta]["positions"].append(novyy_obekt)

        return True
    except ValueError:
        print("Некорректное значение массы")
        return False

def udalit_obekt_po_pozicii(pos):
    world_x = pos[0] - controllable_bg.camera_x
    world_y = pos[1] - controllable_bg.camera_y

    if tekushchiy_rezhim == REZHIM_SBORKI:
        obekty_dlya_udaleniya = vremennye_obekty
    else:
        obekty_dlya_udaleniya = nebesnye_obekty

    if sun.is_alive:
        sun_screen_x, sun_screen_y = controllable_bg.world_to_screen(sun.pos[0], sun.pos[1])
        sun_rect = pygame.Rect(sun_screen_x - sun.radius, sun_screen_y - sun.radius, sun.radius*2, sun.radius*2)
        if sun_rect.collidepoint(pos):
            add_notification("Солнце нельзя удалить!", 2.0)
            return False

    for imya_obekta, dannye_obekta in obekty_dlya_udaleniya.items():
        for i, razmeshchennyy_obekt in enumerate(dannye_obekta["positions"]):
            screen_x, screen_y = controllable_bg.world_to_screen(razmeshchennyy_obekt["pos"][0], razmeshchennyy_obekt["pos"][1])
            obekt_rect_screen = razmeshchennyy_obekt["image"].get_rect(center=(screen_x, screen_y))
            if obekt_rect_screen.collidepoint(pos):
                dannye_obekta["positions"].pop(i)
                print(f"Объект {imya_obekta} удален")
                add_notification(f"{razmeshchennyy_obekt['name_ru']} удален", 1.5)
                return True
    return False

def masshtabirovat_vse_obekty(factor):
    global SCALE_FACTOR, masshtabirovannye_kadry, gif_frames
    SCALE_FACTOR *= factor
    SCALE_FACTOR = max(0.1, min(SCALE_FACTOR, 1.0))

    masshtabirovannye_kadry = []
    for frame in gif_frames:
        masshtabirovannaya_poverhnost = pygame.transform.smoothscale(
            frame,
            (int(frame.get_width() * SCALE_FACTOR), int(frame.get_height() * SCALE_FACTOR)),
        )
        masshtabirovannye_kadry.append(masshtabirovannaya_poverhnost)

    for imya_obekta, dannye_obekta in nebesnye_obekty.items():
        for razmeshchennyy_obekt in dannye_obekta["positions"]:
            masshtabirovat_odin_obekt(razmeshchennyy_obekt, dannye_obekta["image"])

    for imya_obekta, dannye_obekta in vremennye_obekty.items():
        for razmeshchennyy_obekt in dannye_obekta["positions"]:
            masshtabirovat_odin_obekt(razmeshchennyy_obekt, nebesnye_obekty[imya_obekta]["image"])

def masshtabirovat_odin_obekt(obekt, originalnoe_izobrazhenie):
    novyy_razmer = int(obekt["original_size"] * obekt["size_multiplier"] * SCALE_FACTOR)
    masshtabirovannoe_izobrazhenie = pygame.transform.smoothscale(originalnoe_izobrazhenie, (novyy_razmer, novyy_razmer))

    if masshtabirovannoe_izobrazhenie.get_width() != masshtabirovannoe_izobrazhenie.get_height():
        size = max(masshtabirovannoe_izobrazhenie.get_width(), masshtabirovannoe_izobrazhenie.get_height())
        square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        square_surface.fill((0, 0, 0, 0))
        x_offset = (size - masshtabirovannoe_izobrazhenie.get_width()) // 2
        y_offset = (size - masshtabirovannoe_izobrazhenie.get_height()) // 2
        square_surface.blit(masshtabirovannoe_izobrazhenie, (x_offset, y_offset))
        obekt["image"] = make_circular_surface(square_surface)
        obekt["radius"] = novyy_razmer // 2
    else:
        obekt["image"] = make_circular_surface(masshtabirovannoe_izobrazhenie)
        obekt["radius"] = novyy_razmer // 2

def obnovit_fiziku():
    if tekushchiy_rezhim != REZHIM_SIMULYATSII:
        return

    G_grav = 200
    SOFR = 100

    vse_obekty = []

    if sun.is_alive:
        vse_obekty.append({
            "pos": sun.pos,
            "mass": sun.mass,
            "radius": sun.radius,
            "vx": sun.vx,
            "vy": sun.vy,
            "is_star": True,
            "name": "Солнце",
            "obj": sun
        })

    for imya_obekta, dannye_obekta in nebesnye_obekty.items():
        for i, obekt in enumerate(dannye_obekta["positions"]):
            vse_obekty.append({
                "pos": obekt["pos"],
                "mass": obekt["mass"],
                "radius": obekt.get("radius", 20),
                "vx": obekt.get("vx", 0),
                "vy": obekt.get("vy", 0),
                "data": (imya_obekta, i, dannye_obekta),
                "is_star": obekt.get("yavlyaetsya_zvezdoy", False),
                "obekt": obekt,
                "name": obekt.get("name_ru", imya_obekta)
            })

    dt = clock.get_time() / 1000.0 * polzunok_skorosti.poluchit_koefficient_skorosti()
    dt = min(dt, 0.03)

    for obj in vse_obekty:
        ax, ay = 0, 0
        for other in vse_obekty:
            if obj is other:
                continue

            dx = other["pos"][0] - obj["pos"][0]
            dy = other["pos"][1] - obj["pos"][1]
            r2 = dx*dx + dy*dy + SOFR
            r = math.sqrt(r2)

            a = G_grav * other["mass"] / r2

            ax += a * (dx / r)
            ay += a * (dy / r)

        obj["vx"] += ax * dt
        obj["vy"] += ay * dt

    for obj in vse_obekty:
        new_x = obj["pos"][0] + obj["vx"] * dt
        new_y = obj["pos"][1] + obj["vy"] * dt

        obj["pos"][0] = new_x
        obj["pos"][1] = new_y

        if "obekt" in obj:
            obj["obekt"]["pos"][0] = new_x
            obj["obekt"]["pos"][1] = new_y
            obj["obekt"]["vx"] = obj["vx"]
            obj["obekt"]["vy"] = obj["vy"]
        elif "obj" in obj:
            obj["obj"].pos[0] = new_x
            obj["obj"].pos[1] = new_y
            obj["obj"].vx = obj["vx"]
            obj["obj"].vy = obj["vy"]

def proverit_stolknoveniya():
    global sun
    if tekushchiy_rezhim != REZHIM_SIMULYATSII:
        return

    vse_obekty = []

    if sun.is_alive:
        vse_obekty.append({
            "pos": sun.pos,
            "radius": sun.radius,
            "mass": sun.mass,
            "is_star": True,
            "name": "Солнце",
            "vx": sun.vx,
            "vy": sun.vy,
            "obj": sun
        })

    for imya_obekta, dannye_obekta in nebesnye_obekty.items():
        for i, obekt in enumerate(dannye_obekta["positions"]):
            vse_obekty.append({
                "pos": obekt["pos"],
                "radius": obekt.get("radius", 20),
                "mass": obekt["mass"],
                "data": (imya_obekta, i, dannye_obekta),
                "is_star": obekt.get("yavlyaetsya_zvezdoy", False),
                "vx": obekt.get("vx", 0),
                "vy": obekt.get("vy", 0),
                "name": obekt.get("name_ru", imya_obekta),
                "mass_value": obekt.get("mass_value", obekt["mass"] / 10)
            })

    udalennye = set()
    collision_messages = []

    for i in range(len(vse_obekty)):
        for j in range(i + 1, len(vse_obekty)):
            if i in udalennye or j in udalennye:
                continue

            obj1 = vse_obekty[i]
            obj2 = vse_obekty[j]

            dx = obj1["pos"][0] - obj2["pos"][0]
            dy = obj1["pos"][1] - obj2["pos"][1]
            rasstoyanie = math.sqrt(dx*dx + dy*dy)

            if rasstoyanie < (obj1["radius"] + obj2["radius"]):
                if obj1["is_star"] and obj2["is_star"]:
                    if obj1["mass"] > obj2["mass"]:
                        winner, loser = obj1, obj2
                        winner_idx, loser_idx = i, j
                    else:
                        winner, loser = obj2, obj1
                        winner_idx, loser_idx = j, i

                    collision_messages.append(f"Звезда {loser['name']} поглощена звездой {winner['name']}!")

                    if "data" in loser:
                        imya, index, dannye = loser["data"]
                        dannye["positions"].pop(index)
                    udalennye.add(loser_idx)

                    total_mass = winner["mass"] + loser["mass"]
                    winner["vx"] = (winner["vx"] * winner["mass"] + loser["vx"] * loser["mass"]) / total_mass
                    winner["vy"] = (winner["vy"] * winner["mass"] + loser["vy"] * loser["mass"]) / total_mass
                    winner["mass"] = total_mass

                    if "obj" in winner:
                        winner["obj"].mass = total_mass
                        winner["obj"].vx = winner["vx"]
                        winner["obj"].vy = winner["vy"]
                    elif "obekt" in winner:
                        winner["obekt"]["mass"] = total_mass
                        winner["obekt"]["vx"] = winner["vx"]
                        winner["obekt"]["vy"] = winner["vy"]

                    if loser['name'] == "Солнце":
                        sun.is_alive = False
                        sun.saved_pos = sun.pos.copy()
                        collision_messages.append("Солнце погибло! Теперь гравитацию определяют другие звезды.")

                elif obj1.get("is_star", False) or obj2.get("is_star", False):
                    star = obj1 if obj1.get("is_star", False) else obj2
                    planet = obj2 if star is obj1 else obj1

                    collision_messages.append(f"{planet['name']} поглощена звездой {star['name']}")

                    if "data" in planet:
                        imya, index, dannye = planet["data"]
                        dannye["positions"].pop(index)
                    udalennye.add(j if star is obj1 else i)

                    star["mass"] += planet["mass"] * 0.01
                    if "obj" in star:
                        star["obj"].mass = star["mass"]

                else:
                    if obj1["mass"] > obj2["mass"] * 3:
                        collision_messages.append(f"{obj2['name']} поглощен {obj1['name']}")
                        if "data" in obj2:
                            imya2, index2, dannye2 = obj2["data"]
                            dannye2["positions"].pop(index2)
                        udalennye.add(j)

                        obj1["mass"] += obj2["mass"] * 0.8
                        if "obekt" in obj1:
                            obj1["obekt"]["mass"] = obj1["mass"]

                    elif obj2["mass"] > obj1["mass"] * 3:
                        collision_messages.append(f"{obj1['name']} поглощен {obj2['name']}")
                        if "data" in obj1:
                            imya1, index1, dannye1 = obj1["data"]
                            dannye1["positions"].pop(index1)
                        udalennye.add(i)

                        obj2["mass"] += obj1["mass"] * 0.8
                        if "obekt" in obj2:
                            obj2["obekt"]["mass"] = obj2["mass"]

                    else:
                        collision_messages.append(f"{obj1['name']} и {obj2['name']} столкнулись и разрушились")
                        if i not in udalennye and "data" in obj1:
                            imya1, index1, dannye1 = obj1["data"]
                            dannye1["positions"].pop(index1)
                            udalennye.add(i)
                        if j not in udalennye and "data" in obj2:
                            imya2, index2, dannye2 = obj2["data"]
                            dannye2["positions"].pop(index2)
                            udalennye.add(j)

    for msg in collision_messages[:3]:
        add_notification(msg, 2.5)

def narisovat_knopku_start_stop():
    global knopka_start
    knopka_start.centerx = tekushaya_shirina // 2
    knopka_start.y = tekushaya_vysota - 150

    if tekushchiy_rezhim == REZHIM_SBORKI:
        text = "СТАРТ"
        color = knopka_start_navedenie_cvet if knopka_start.collidepoint(poziciya_myshi) else knopka_start_cvet
    else:
        text = "СТОП"
        color = (200, 0, 0) if knopka_start.collidepoint(poziciya_myshi) else (150, 0, 0)

    pygame.draw.rect(screen, color, knopka_start, border_radius=5)
    pygame.draw.rect(screen, WHITE, knopka_start, 2, border_radius=5)

    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=knopka_start.center)
    screen.blit(text_surf, text_rect)

def narisovat_knopku(rect, label):
    color = knopka_navedenie_cvet if rect.collidepoint(poziciya_myshi) else knopka_cvet
    pygame.draw.rect(screen, color, rect, border_radius=5)
    text = font.render(label, True, WHITE)
    text_rect = text.get_rect(center=rect.center)
    screen.blit(text, text_rect)

def narisovat_indikator_rezhima():
    if tekushchiy_rezhim == REZHIM_SBORKI:
        text = "РЕЖИМ СБОРКИ"
        color = YELLOW
    elif tekushchiy_rezhim == REZHIM_SIMULYATSII:
        text = "РЕЖИМ СИМУЛЯЦИИ"
        color = GREEN
    else:
        return

    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(topright=(tekushaya_shirina - 130, 20))

    bg_rect = text_rect.inflate(20, 10)
    pygame.draw.rect(screen, BLACK, bg_rect, border_radius=5)
    pygame.draw.rect(screen, color, bg_rect, 2, border_radius=5)

    screen.blit(text_surf, text_rect)


def narisovat_knopku_menu():
    knopka_menu = pygame.Rect(tekushaya_shirina - 110, 22, 100, 36)
    color = (100, 100, 200) if knopka_menu.collidepoint(poziciya_myshi) else (50, 50, 150)
    pygame.draw.rect(screen, color, knopka_menu, border_radius=5)
    pygame.draw.rect(screen, WHITE, knopka_menu, 2, border_radius=5)

    text_surf = small_font.render("МЕНЮ", True, WHITE)
    text_rect = text_surf.get_rect(center=knopka_menu.center)
    screen.blit(text_surf, text_rect)

    return knopka_menu

def show_start_screen():
    global tekushchiy_rezhim, tekushaya_shirina, tekushaya_vysota, screen

    start_background = pygame.image.load('космос.jpg').convert()
    start_background = pygame.transform.scale(start_background, (tekushaya_shirina, tekushaya_vysota))

    button_play = pygame.Rect(tekushaya_shirina//2 - 100, tekushaya_vysota//2 - 60, 200, 50)
    button_help = pygame.Rect(tekushaya_shirina//2 - 100, tekushaya_vysota//2 + 10, 200, 50)
    button_info = pygame.Rect(tekushaya_shirina//2 - 100, tekushaya_vysota//2 + 80, 200, 50)

    help_text = [
        "Управление:",
        "ЛКМ - выбор и размещение объектов",
        "ПКМ - удаление объекта",
        "Зажать ЛКМ на фоне - перемещение камеры",
        "Скролл скорости - ускорение времени",
        "Кнопки + и - - масштабирование объектов",
        "СТАРТ - запуск физической симуляции",
        "СТОП - возврат в режим сборки (Солнце остается на месте)",
        "МЕНЮ - возврат в главное меню",
        "",
        "Совет: Если Солнце погибло, другие звезды станут центрами гравитации!"
    ]

    info_text = [
        "Объекты и их особенности:",
        "",
        "Железная планета - плотная, сильное магнитное поле",
        "Газовая планета - низкая плотность, огромные размеры",
        "Ледяная планета - покрыта льдом, возможна жизнь",
        "",
        "Сверхгигант - огромная звезда, короткий срок жизни",
        "Гигант - расширившаяся звезда",
        "Белый карлик - очень плотная остывшая звезда",
        "",
        "Астероиды: Металлический, Силикатный, Углеродный",
        "",
        "Масса планет и астероидов измеряется в массах Земли",
        "Масса звезд измеряется в массах Солнца"
    ]

    show_help = False
    show_info = False

    while True:
        current_width, current_height = screen.get_size()
        start_background = pygame.image.load('космос.jpg').convert()
        start_background = pygame.transform.scale(start_background, (current_width, current_height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                tekushaya_shirina, tekushaya_vysota = event.w, event.h
                screen = pygame.display.set_mode((tekushaya_shirina, tekushaya_vysota), pygame.RESIZABLE)
                button_play = pygame.Rect(tekushaya_shirina//2 - 100, tekushaya_vysota//2 - 60, 200, 50)
                button_help = pygame.Rect(tekushaya_shirina//2 - 100, tekushaya_vysota//2 + 10, 200, 50)
                button_info = pygame.Rect(tekushaya_shirina//2 - 100, tekushaya_vysota//2 + 80, 200, 50)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.collidepoint(event.pos):
                    tekushchiy_rezhim = REZHIM_SBORKI
                    return True
                elif button_help.collidepoint(event.pos):
                    show_help = True
                    show_info = False
                elif button_info.collidepoint(event.pos):
                    show_info = True
                    show_help = False
                elif show_help or show_info:
                    show_help = False
                    show_info = False

        screen.blit(start_background, (0, 0))

        title = big_font.render("КОСМИЧЕСКИЙ СИМУЛЯТОР", True, YELLOW)
        title_rect = title.get_rect(center=(tekushaya_shirina//2, tekushaya_vysota//2 - 150))
        screen.blit(title, title_rect)

        mouse_pos = pygame.mouse.get_pos()

        for button, text in [(button_play, "ИГРАТЬ"), (button_help, "СПРАВКА"), (button_info, "ОПИСАНИЕ")]:
            color = (100, 100, 200) if button.collidepoint(mouse_pos) else (50, 50, 100)
            pygame.draw.rect(screen, color, button, border_radius=10)
            pygame.draw.rect(screen, WHITE, button, 2, border_radius=10)
            text_surf = font.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=button.center)
            screen.blit(text_surf, text_rect)

        if show_help:
            help_surface = pygame.Surface((tekushaya_shirina - 200, 450), pygame.SRCALPHA)
            help_surface.fill((0, 0, 0, 200))
            pygame.draw.rect(help_surface, WHITE, help_surface.get_rect(), 2, border_radius=10)

            y_offset = 20
            for line in help_text:
                text_surf = small_font.render(line, True, YELLOW)
                help_surface.blit(text_surf, (20, y_offset))
                y_offset += 30

            screen.blit(help_surface, (100, tekushaya_vysota//2 - 225))

        if show_info:
            info_surface = pygame.Surface((tekushaya_shirina - 200, 500), pygame.SRCALPHA)
            info_surface.fill((0, 0, 0, 200))
            pygame.draw.rect(info_surface, WHITE, info_surface.get_rect(), 2, border_radius=10)

            y_offset = 20
            for line in info_text:
                text_surf = small_font.render(line, True, YELLOW)
                info_surface.blit(text_surf, (20, y_offset))
                y_offset += 25

            screen.blit(info_surface, (100, tekushaya_vysota//2 - 250))

        esc_text = small_font.render("Нажмите ESC для выхода", True, WHITE)
        esc_rect = esc_text.get_rect(bottomright=(tekushaya_shirina - 20, tekushaya_vysota - 20))
        screen.blit(esc_text, esc_rect)

        pygame.display.flip()
        clock.tick(60)

polzunok_skorosti = PolzunokSkorosti(20, HEIGHT - 80, 200, 20)
controllable_bg.set_polzunok(polzunok_skorosti)

if not show_start_screen():
    pygame.quit()
    exit()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        controllable_bg.handle_event(event)

        if event.type == pygame.VIDEORESIZE:
            tekushaya_shirina, tekushaya_vysota = event.w, event.h
            screen = pygame.display.set_mode((tekushaya_shirina, tekushaya_vysota), pygame.RESIZABLE)
            polzunok_skorosti.pryamougolnik.y = tekushaya_vysota - 80

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if rezhim_vvoda != 0:
                    rezhim_vvoda = 0
                    ozhidaemyy_obekt = None
                    vvedennyy_text = ""
                    ozhidaemaya_massa = None
                    print("Ввод отменен")
                else:
                    running = False

            if rezhim_vvoda == 1:
                if event.key == pygame.K_RETURN:
                    try:
                        znachenie_massy = float(vvedennyy_text)
                        znachenie_massy = max(0.1, min(znachenie_massy, 100))
                        ozhidaemaya_massa = znachenie_massy
                        rezhim_vvoda = 0
                        print(f"Масса сохранена: {ozhidaemaya_massa}. Теперь кликните на экран для размещения объекта")
                    except ValueError:
                        print("Некорректное значение массы. Попробуйте еще раз.")
                        vvedennyy_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    vvedennyy_text = vvedennyy_text[:-1]
                else:
                    if event.unicode.isdigit() or event.unicode == '.':
                        vvedennyy_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            plyus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 - knopka_shirina - 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)
            minus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 + 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)

            knopka_start.centerx = tekushaya_shirina // 2
            knopka_start.y = tekushaya_vysota - 150

            knopka_menu = pygame.Rect(tekushaya_shirina - 110, 22, 100, 36)

            if event.button == 1:
                if knopka_menu.collidepoint(pos):
                    vernutsya_v_glavnoe_menu()
                    if not show_start_screen():
                        running = False
                    continue

                if knopka_start.collidepoint(pos):
                    if tekushchiy_rezhim == REZHIM_SBORKI:
                        zapustit_simulyatsiyu()
                    else:
                        vernutsya_v_sborku()
                    continue

                if polzunok_skorosti.rucka_pryamougolnik().collidepoint(pos):
                    continue

                if plyus_pryamougolnik.collidepoint(pos):
                    masshtabirovat_vse_obekty(1.1)
                    continue
                elif minus_pryamougolnik.collidepoint(pos):
                    masshtabirovat_vse_obekty(0.9)
                    continue

                menu_y = 10
                menu_width = 60
                menu_height = 30
                main_rects = [
                    pygame.Rect(10, menu_y, menu_width, menu_height),
                    pygame.Rect(10 + menu_width + 10, menu_y, menu_width, menu_height),
                    pygame.Rect(10 + 2*(menu_width + 10), menu_y, menu_width, menu_height)
                ]
                click_na_menu = False
                for i, item in enumerate(menus["main"]):
                    item["rect"] = main_rects[i]
                    if item["rect"].collidepoint(pos):
                        click_na_menu = True
                        break

                if not click_na_menu and tekushchee_menu != "main":
                    y_offset = 40
                    menu_item_height = 30
                    for item in menus[tekushchee_menu]:
                        item["rect"] = pygame.Rect(10, y_offset, 250, menu_item_height)
                        if item["rect"].collidepoint(pos):
                            click_na_menu = True
                            break
                        y_offset += menu_item_height + 5

                obrabotat_nazhatie_menu(pos)

                if not click_na_menu and not (plyus_pryamougolnik.collidepoint(pos) or minus_pryamougolnik.collidepoint(pos)):
                    if rezhim_vvoda == 0 and ozhidaemyy_obekt is not None and ozhidaemaya_massa is not None:
                        if razmestit_obekt_s_massoy(pos, ozhidaemyy_obekt, ozhidaemaya_massa):
                            ozhidaemyy_obekt = None
                            ozhidaemaya_massa = None
                            print("Объект успешно размещен! Выберите следующий объект для размещения.")
                    else:
                        if ozhidaemyy_obekt is None:
                            print("Сначала выберите объект из меню (Планеты, Звезды или Астероиды)")
                        elif ozhidaemaya_massa is None:
                            print("Сначала введите массу объекта и нажмите Enter")

            elif event.button == 3:
                click_na_ui = False
                if plyus_pryamougolnik.collidepoint(pos) or minus_pryamougolnik.collidepoint(pos) or polzunok_skorosti.rucka_pryamougolnik().collidepoint(pos):
                    click_na_ui = True

                menu_y = 10
                menu_width = 60
                menu_height = 30
                main_rects = [
                    pygame.Rect(10, menu_y, menu_width, menu_height),
                    pygame.Rect(10 + menu_width + 10, menu_y, menu_width, menu_height),
                    pygame.Rect(10 + 2*(menu_width + 10), menu_y, menu_width, menu_height)
                ]
                for i, item in enumerate(menus["main"]):
                    item["rect"] = main_rects[i]
                    if item["rect"].collidepoint(pos):
                        click_na_ui = True
                        break

                if not click_na_ui and tekushchee_menu != "main":
                    y_offset = 40
                    menu_item_height = 30
                    for item in menus[tekushchee_menu]:
                        item["rect"] = pygame.Rect(10, y_offset, 250, menu_item_height)
                        if item["rect"].collidepoint(pos):
                            click_na_ui = True
                            break
                        y_offset += menu_item_height + 5

                if not click_na_ui and pos[1] > 80:
                    if udalit_obekt_po_pozicii(pos):
                        print("Объект удален")

    controllable_bg.draw(screen, tekushaya_shirina, tekushaya_vysota)

    poziciya_myshi = pygame.mouse.get_pos()
    knopki_myshi = pygame.mouse.get_pressed()

    polzunok_skorosti.obnovit(poziciya_myshi, knopki_myshi)

    menu_y = 10
    menu_width = 60
    menu_height = 30
    main_rects = [
        pygame.Rect(10, menu_y, menu_width, menu_height),
        pygame.Rect(10 + menu_width + 10, menu_y, menu_width, menu_height),
        pygame.Rect(10 + 2*(menu_width + 10), menu_y, menu_width, menu_height)
    ]
    for i, item in enumerate(menus["main"]):
        item["rect"] = main_rects[i]
        navedenie = item["rect"].collidepoint(poziciya_myshi)
        narisovat_text_ili_ikonu(item, item["rect"], navedenie)

    if tekushchee_menu != "main":
        y_offset = 40
        menu_item_height = 30
        for item in menus[tekushchee_menu]:
            item["rect"] = pygame.Rect(10, y_offset, 250, menu_item_height)
            navedenie = item["rect"].collidepoint(poziciya_myshi)
            narisovat_text_ili_ikonu(item, item["rect"], navedenie)
            y_offset += menu_item_height + 5

    if tekushchiy_rezhim == REZHIM_SIMULYATSII:
        obnovit_fiziku()
        proverit_stolknoveniya()

    if sun.is_alive:
        frame = masshtabirovannye_kadry[tekushiy_kadr]
        sun_screen_x, sun_screen_y = controllable_bg.world_to_screen(sun.pos[0], sun.pos[1])
        x = sun_screen_x - frame.get_width() // 2
        y = sun_screen_y - frame.get_height() // 2
        screen.blit(frame, (x, y))
    else:
        sun_screen_x, sun_screen_y = controllable_bg.world_to_screen(sun.pos[0], sun.pos[1])
        dead_text = font.render ("", True, RED)
        dead_rect = dead_text.get_rect(center=(sun_screen_x, sun_screen_y))
        screen.blit(dead_text, dead_rect)

    if tekushchiy_rezhim == REZHIM_SBORKI:
        obekty_dlya_otrisovki = vremennye_obekty
    else:
        obekty_dlya_otrisovki = nebesnye_obekty

    for imya_obekta, dannye_obekta in obekty_dlya_otrisovki.items():
        for razmeshchennyy_obekt in dannye_obekta["positions"]:
            screen_x, screen_y = controllable_bg.world_to_screen(razmeshchennyy_obekt["pos"][0], razmeshchennyy_obekt["pos"][1])
            img_rect = razmeshchennyy_obekt["image"].get_rect(center=(screen_x, screen_y))
            screen.blit(razmeshchennyy_obekt["image"], img_rect)

    now = pygame.time.get_ticks()
    if now - poslednee_obnovlenie > zaderzhka_kadra:
        tekushiy_kadr = (tekushiy_kadr + 1) % len(masshtabirovannye_kadry)
        poslednee_obnovlenie = now

    if rezhim_vvoda != 0:
        s = pygame.Surface((tekushaya_shirina, tekushaya_vysota), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        input_rect = pygame.Rect(tekushaya_shirina // 2 - 150, tekushaya_vysota // 2 - 50, 300, 50)
        pygame.draw.rect(screen, WHITE, input_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, input_rect, 2, border_radius=10)
        prompt_surf = font.render(tekushchiy_zapros, True, YELLOW)
        prompt_rect = prompt_surf.get_rect(center=(tekushaya_shirina // 2, tekushaya_vysota // 2 - 80))
        prompt_shadow = font.render(tekushchiy_zapros, True, BLACK)
        shadow_rect = prompt_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        screen.blit(prompt_shadow, shadow_rect)
        screen.blit(prompt_surf, prompt_rect)

        text_surf = font.render(vvedennyy_text, True, BLACK)
        text_rect = text_surf.get_rect(center=input_rect.center)
        screen.blit(text_surf, text_rect)

    notification_manager.update()
    notification_manager.draw(screen, tekushaya_shirina)

    narisovat_knopku_start_stop()
    polzunok_skorosti.narisovat(screen)

    knopka_menu = narisovat_knopku_menu()

    plyus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 - knopka_shirina - 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)
    minus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 + 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)
    narisovat_knopku(plyus_pryamougolnik, "+")
    narisovat_knopku(minus_pryamougolnik, "-")

    narisovat_indikator_rezhima()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()