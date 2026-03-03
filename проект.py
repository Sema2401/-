import pygame
from PIL import Image
import math
import random

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
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 150, 255)
LIGHT_BLUE = (150, 200, 255)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 0)
RED = (255, 100, 100)
POLZUNOK_CVET = (100, 100, 255)
POLZUNOK_RUCHKA_CVET = (200, 200, 255)

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

background_original = pygame.image.load('cosmos.jpg').convert()
background = pygame.transform.scale(background_original, (tekushaya_shirina, tekushaya_vysota))

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
        self.skorost = 500
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

        skorost_text = small_font.render(f"Скорость: {self.skorost:.1f}", True, YELLOW)
        text_rect = skorost_text.get_rect(midleft=(self.pryamougolnik.right + 10, self.pryamougolnik.centery))
        screen.blit(skorost_text, text_rect)

    def poluchit_koefficient_skorosti(self):
        return self.skorost / 50.0

def zagruzit_i_sdelat_kruglym(path, size):
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.scale(image, (size, size))
    return make_circular_surface(image)

koficzienty_razmera_zvezd = {
    "Sverhgiant": 1.4,
    "Gigant": 1.0,
    "Belyy_karlik": 0.8,
}

imena_zvezd = set(koficzienty_razmera_zvezd.keys())

nebesnye_obekty = {
    "zheleznaya_planeta": {"image": zagruzit_i_sdelat_kruglym('Железная планета.png', 120), "base_size": 120, "positions": []},
    "gazovaya_planeta": {"image": zagruzit_i_sdelat_kruglym('Газовая планета.png', 180), "base_size": 180, "positions": []},
    "ledyanaya_planeta": {"image": zagruzit_i_sdelat_kruglym('Ледяная планета.png', 140), "base_size": 140, "positions": []},
    "Sverhgiant": {"image": zagruzit_i_sdelat_kruglym('Сверхгигант.png', int(solnce_original_razmer * koficzienty_razmera_zvezd["Sverhgiant"] * 0.7)),
               "base_size": int(solnce_original_razmer * koficzienty_razmera_zvezd["Sverhgiant"] * 0.7), "positions": []},
    "Gigant": {"image": zagruzit_i_sdelat_kruglym('Гигант.png', int(solnce_original_razmer * koficzienty_razmera_zvezd["Gigant"] * 0.7)),
                "base_size": int(solnce_original_razmer * koficzienty_razmera_zvezd["Gigant"] * 0.7), "positions": []},
    "Belyy_karlik": {"image": zagruzit_i_sdelat_kruglym('Белый карлик.png', int(solnce_original_razmer * koficzienty_razmera_zvezd["Belyy_karlik"] * 0.7)),
                 "base_size": int(solnce_original_razmer * koficzienty_razmera_zvezd["Belyy_karlik"] * 0.7), "positions": []},
    "Metallicheskii": {"image": zagruzit_i_sdelat_kruglym('Металлический.png', 140), "base_size": 140, "positions": []},
    "Siikatnii": {"image": zagruzit_i_sdelat_kruglym('Силикатный.png', 140), "base_size": 140, "positions": []},
    "Uglerodnii": {"image": zagruzit_i_sdelat_kruglym('Углеродный.png', 140), "base_size": 140, "positions": []},
}

vybrannyy_obekt = None
tekushchee_menu = "main"
menus = {}

rezhim_vvoda = 0
vvedennyy_text = ""
zapros_massy = "Введите массу объекта (в массах Земли):"
tekushchiy_zapros = zapros_massy
ozhidaemyy_obekt = None
ozhidaemaya_massa = None


def vybrat_obekt(imya_obekta):
    global rezhim_vvoda, ozhidaemyy_obekt, tekushchiy_zapros, vvedennyy_text
    ozhidaemyy_obekt = imya_obekta
    rezhim_vvoda = 1
    vvedennyy_text = ""
    if imya_obekta in imena_zvezd:
        tekushchiy_zapros = "Введите массу объекта (в массах Солнца):"
    else:
        tekushchiy_zapros = zapros_massy

def sozdat_menyu():
    global menus
    menus["main"] = [
        {"text": "Планеты", "submenu": "planets", "icon": planeta_ikona},
        {"text": "Звезды", "submenu": "stars", "icon": zvezda_ikona},
        {"text": "Астероид", "submenu": "asteroid", "icon": asteroid_ikona},
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
        if len(item["text"]) > 15:
            text_surf = small_font.render(item["text"], True, color)
        else:
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

def razmestit_obekt_s_massoy(pos, imya_obekta, massa):
    try:
        znachenie_massy = float(massa)
        znachenie_massy = max(0.1, min(znachenie_massy, 100))
        if imya_obekta in imena_zvezd:
            mnozhitel_razmera = 1.0 + (znachenie_massy ** 0.5) * 0.5
        else:
            mnozhitel_razmera = 0.8 + (znachenie_massy ** 0.5) / 8

        dannye_obekta = nebesnye_obekty[imya_obekta]
        bazovyy_razmer = dannye_obekta["base_size"]
        novyy_razmer = int(bazovyy_razmer * mnozhitel_razmera * SCALE_FACTOR)
        originalnoe_izobrazhenie = dannye_obekta["image"]
        masshtabirovannoe_izobrazhenie = pygame.transform.smoothscale(originalnoe_izobrazhenie, (novyy_razmer, novyy_razmer))

        poziciya_solnca = [tekushaya_shirina // 2, tekushaya_vysota // 2]

        dx = pos[0] - poziciya_solnca[0]
        dy = pos[1] - poziciya_solnca[1]
        rasstoyanie = math.sqrt(dx*dx + dy*dy)

        nachalnyy_ugol = math.atan2(dy, dx)

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

        dannye_obekta["positions"].append({
            "pos": [pos[0], pos[1]],
            "image": masshtabirovannoe_izobrazhenie,
            "mass": znachenie_massy,
            "original_size": bazovyy_razmer,
            "size_multiplier": mnozhitel_razmera,
            "rasstoyanie": rasstoyanie,
            "ugol": nachalnyy_ugol,
            "skorost_vrasheniya": 0.02
        })
        return True
    except ValueError:
        print("Некорректное значение массы")
        return False

def udalit_obekt_po_pozicii(pos):
    for imya_obekta, dannye_obekta in nebesnye_obekty.items():
        for i, razmeshchennyy_obekt in enumerate(dannye_obekta["positions"]):
            obekt_rect = razmeshchennyy_obekt["image"].get_rect(center=razmeshchennyy_obekt["pos"])
            if obekt_rect.collidepoint(pos):
                dannye_obekta["positions"].pop(i)
                return True
    return False

def masshtabirovat_vse_obekty(factor):
    global SCALE_FACTOR, masshtabirovannye_kadry, gif_frames
    SCALE_FACTOR *= factor
    SCALE_FACTOR = max(0.1, min(SCALE_FACTOR, 1.0))  # Изменили максимальный масштаб
    masshtabirovannye_kadry = []
    for frame in gif_frames:
        masshtabirovannaya_poverhnost = pygame.transform.smoothscale(
            frame,
            (int(frame.get_width() * SCALE_FACTOR), int(frame.get_height() * SCALE_FACTOR)),
        )
        masshtabirovannye_kadry.append(masshtabirovannaya_poverhnost)
    for imya_obekta, dannye_obekta in nebesnye_obekty.items():
        for razmeshchennyy_obekt in dannye_obekta["positions"]:
            novyy_razmer = int(razmeshchennyy_obekt["original_size"] * razmeshchennyy_obekt["size_multiplier"] * SCALE_FACTOR)
            originalnoe_izobrazhenie = dannye_obekta["image"]
            masshtabirovannoe_izobrazhenie = pygame.transform.smoothscale(originalnoe_izobrazhenie, (novyy_razmer, novyy_razmer))
            if masshtabirovannoe_izobrazhenie.get_width() != masshtabirovannoe_izobrazhenie.get_height():
                size = max(masshtabirovannoe_izobrazhenie.get_width(), masshtabirovannoe_izobrazhenie.get_height())
                square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                square_surface.fill((0, 0, 0, 0))
                x_offset = (size - masshtabirovannoe_izobrazhenie.get_width()) // 2
                y_offset = (size - masshtabirovannoe_izobrazhenie.get_height()) // 2
                square_surface.blit(masshtabirovannoe_izobrazhenie, (x_offset, y_offset))
                razmeshchennyy_obekt["image"] = make_circular_surface(square_surface)
            else:
                razmeshchennyy_obekt["image"] = make_circular_surface(masshtabirovannoe_izobrazhenie)

def pereschitat_pozicii_obektov(old_width, old_height, new_width, new_height):
    for imya_obekta, dannye_obekta in nebesnye_obekty.items():
        for razmeshchennyy_obekt in dannye_obekta["positions"]:
            staraya_x, staraya_y = razmeshchennyy_obekt["pos"]
            norm_x = staraya_x / old_width
            norm_y = staraya_y / old_height

            novaya_x = norm_x * new_width
            novaya_y = norm_y * new_height

            razmeshchennyy_obekt["pos"][0] = novaya_x
            razmeshchennyy_obekt["pos"][1] = novaya_y

G = 0.5
SMYAGCHENIE = 100.0
MASSA_SOLNCA = 10000

def obnovit_orbity():
    poziciya_solnca = [tekushaya_shirina // 2, tekushaya_vysota // 2]
    koefficient_skorosti = polzunok_skorosti.poluchit_koefficient_skorosti()

    for imya_obekta, dannye_obekta in nebesnye_obekty.items():
        for obekt in dannye_obekta["positions"]:
            if "ugol" in obekt and "rasstoyanie" in obekt:
                skorost_vrasheniya = 0.03 / math.sqrt(obekt["rasstoyanie"] / 100) * koefficient_skorosti
                obekt["ugol"] += skorost_vrasheniya * dt

                obekt["pos"][0] = poziciya_solnca[0] + obekt["rasstoyanie"] * math.cos(obekt["ugol"])
                obekt["pos"][1] = poziciya_solnca[1] + obekt["rasstoyanie"] * math.sin(obekt["ugol"])

polzunok_skorosti = PolzunokSkorosti(20, HEIGHT - 80, 200, 20)

running = True
while running:
    dt = clock.get_time() / 1000.0
    dt = min(dt, 0.05)

    screen.blit(background, (0, 0))
    poziciya_myshi = pygame.mouse.get_pos()
    knopki_myshi = pygame.mouse.get_pressed()

    polzunok_skorosti.obnovit(poziciya_myshi, knopki_myshi)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            staraya_shirina, staraya_vysota = tekushaya_shirina, tekushaya_vysota
            tekushaya_shirina, tekushaya_vysota = event.w, event.h
            screen = pygame.display.set_mode((tekushaya_shirina, tekushaya_vysota), pygame.RESIZABLE)

            pereschitat_pozicii_obektov(staraya_shirina, staraya_vysota, tekushaya_shirina, tekushaya_vysota)
            polzunok_skorosti.pryamougolnik.y = tekushaya_vysota - 80
            background = pygame.transform.scale(background_original, (tekushaya_shirina, tekushaya_vysota))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if rezhim_vvoda != 0:
                    rezhim_vvoda = 0
                    ozhidaemyy_obekt = None
                    vvedennyy_text = ""
                else:
                    running = False

            if rezhim_vvoda == 1:
                if event.key == pygame.K_RETURN:
                    try:
                        znachenie_massy = float(vvedennyy_text)
                        znachenie_massy = max(0.1, min(znachenie_massy, 100))
                        ozhidaemaya_massa = znachenie_massy
                        rezhim_vvoda = 0
                        vvedennyy_text = ""
                    except ValueError:
                        vvedennyy_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    vvedennyy_text = vvedennyy_text[:-1]
                else:
                    if event.unicode.isdigit() or event.unicode == '.' or event.unicode == '-':
                        vvedennyy_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            plyus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 - knopka_shirina - 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)
            minus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 + 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)

            if event.button == 1:
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

                if not click_na_menu and not (plyus_pryamougolnik.collidepoint(pos) or minus_pryamougolnik.collidepoint(pos)) and rezhim_vvoda == 0 and ozhidaemyy_obekt is not None and ozhidaemaya_massa is not None and pos[1] > 80:
                    if razmestit_obekt_s_massoy(pos, ozhidaemyy_obekt, ozhidaemaya_massa):
                        ozhidaemyy_obekt = None
                        ozhidaemaya_massa = None

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

    obnovit_orbity()

    for imya_obekta, dannye_obekta in nebesnye_obekty.items():
        for razmeshchennyy_obekt in dannye_obekta["positions"]:
            img_rect = razmeshchennyy_obekt["image"].get_rect(center=razmeshchennyy_obekt["pos"])
            screen.blit(razmeshchennyy_obekt["image"], img_rect)

    now = pygame.time.get_ticks()
    if now - poslednee_obnovlenie > zaderzhka_kadra:
        tekushiy_kadr = (tekushiy_kadr + 1) % len(masshtabirovannye_kadry)
        poslednee_obnovlenie = now
    frame = masshtabirovannye_kadry[tekushiy_kadr]
    x = (tekushaya_shirina - frame.get_width()) // 2
    y = (tekushaya_vysota - frame.get_height()) // 2
    screen.blit(frame, (x, y))

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

        inst_surf = small_font.render("Нажмите Enter для подтверждения", True, YELLOW)
        inst_rect = inst_surf.get_rect(center=(tekushaya_shirina // 2, tekushaya_vysota // 2 + 30))
        inst_shadow = small_font.render("Нажмите Enter для подтверждения", True, BLACK)
        shadow_rect = inst_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        screen.blit(inst_shadow, shadow_rect)
        screen.blit(inst_surf, inst_rect)

    def narisovat_knopku(rect, label, podskazka=""):
        color = knopka_navedenie_cvet if rect.collidepoint(poziciya_myshi) else knopka_cvet
        pygame.draw.rect(screen, color, rect, border_radius=5)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        if podskazka and rect.collidepoint(poziciya_myshi):
            podskazka_surf = small_font.render(podskazka, True, WHITE)
            podskazka_rect = podskazka_surf.get_rect(midbottom=(rect.centerx, rect.top - 5))
            pygame.draw.rect(screen, BLACK, podskazka_rect.inflate(10, 5), border_radius=3)
            screen.blit(podskazka_surf, podskazka_rect)

    polzunok_skorosti.narisovat(screen)

    plyus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 - knopka_shirina - 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)
    minus_pryamougolnik = pygame.Rect(tekushaya_shirina // 2 + 20, tekushaya_vysota - 80, knopka_shirina, knopka_vysota)
    narisovat_knopku(plyus_pryamougolnik, "+")
    narisovat_knopku(minus_pryamougolnik, "-")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()