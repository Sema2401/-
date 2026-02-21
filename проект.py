import pygame
from PIL import Image
import math

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

WIDTH, HEIGHT = 800, 600
current_width, current_height = WIDTH, HEIGHT
screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 150, 255)
LIGHT_BLUE = (150, 200, 255)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 0)
RED = (255, 100, 100)

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

background_original = pygame.image.load('cosmos.jpg').convert()
background = pygame.transform.scale(background_original, (current_width, current_height))

GIF_PATH = "sun.gif"
pil_frames = extract_gif_frames(GIF_PATH)
gif_frames = load_frames_as_surfaces(pil_frames)
sun_original_size = gif_frames[0].get_width()

SCALE_FACTOR = 0.5
scaled_frames = []
for frame in gif_frames:
    scaled_surface = pygame.transform.smoothscale(frame, (int(frame.get_width() * SCALE_FACTOR), int(frame.get_height() * SCALE_FACTOR)))
    scaled_frames.append(scaled_surface)

button_width, button_height = 100, 50
button_color = (50, 50, 50)
hover_color = (100, 100, 100)

current_frame = 0
frame_delay = 100
last_update = pygame.time.get_ticks()

planet_icon = pygame.image.load('значок_планеты.jpg').convert_alpha()
planet_icon = pygame.transform.scale(planet_icon, (67, 50))
star_icon = pygame.image.load('значок_звезды.webp').convert_alpha()
star_icon = pygame.transform.scale(star_icon, (74, 50))
asteroid_icon = pygame.image.load('значок_астероида.webp').convert_alpha()
asteroid_icon = pygame.transform.scale(asteroid_icon, (67, 50))

def load_and_make_circular(path, size):
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.scale(image, (size, size))
    return make_circular_surface(image)

star_size_factors = {
    "sirius": 2.5,
    "canopus": 1.8,
    "arcturus": 1.6,
    "vega": 1.4,
    "aldebaran": 1.5
}

celestial_objects = {
    "earth": {"image": load_and_make_circular('Земля.png', 180), "base_size": 180, "positions": []},
    "mercury": {"image": load_and_make_circular('Меркурий.png', 140), "base_size": 140, "positions": []},
    "venus": {"image": load_and_make_circular('Венера.png', 140), "base_size": 140, "positions": []},
    "mars": {"image": load_and_make_circular('Марс.png', 130), "base_size": 130, "positions": []},
    "jupiter": {"image": load_and_make_circular('Юпитер.png', 220), "base_size": 220, "positions": []},
    "saturn": {"image": load_and_make_circular('Сатурн.png', 260), "base_size": 260, "positions": []},
    "uranium": {"image": load_and_make_circular('Уран.png', 240), "base_size": 240, "positions": []},
    "neptune": {"image": load_and_make_circular('Нептун.png', 180), "base_size": 180, "positions": []},
    "sirius": {"image": load_and_make_circular('Сириус.png', int(sun_original_size * star_size_factors["sirius"])),
               "base_size": int(sun_original_size * star_size_factors["sirius"]), "positions": []},
    "canopus": {"image": load_and_make_circular('Канопус.png', int(sun_original_size * star_size_factors["canopus"])),
                "base_size": int(sun_original_size * star_size_factors["canopus"]), "positions": []},
    "arcturus": {"image": load_and_make_circular('Арктур.png', int(sun_original_size * star_size_factors["arcturus"])),
                 "base_size": int(sun_original_size * star_size_factors["arcturus"]), "positions": []},
    "vega": {"image": load_and_make_circular('Вега.png', int(sun_original_size * star_size_factors["vega"])),
             "base_size": int(sun_original_size * star_size_factors["vega"]), "positions": []},
    "aldebaran": {"image": load_and_make_circular('Альдебаран.png', int(sun_original_size * star_size_factors["aldebaran"])),
                  "base_size": int(sun_original_size * star_size_factors["aldebaran"]), "positions": []},
    "psyche": {"image": load_and_make_circular('16 Психея.png', 180), "base_size": 180, "positions": []},
    "dimorph": {"image": load_and_make_circular('Диморф.png', 180), "base_size": 180, "positions": []},
    "bennu": {"image": load_and_make_circular('Бенну.png', 180), "base_size": 180, "positions": []},
    "ryugu": {"image": load_and_make_circular('Рюгу.png', 180), "base_size": 180, "positions": []},
    "ceres": {"image": load_and_make_circular('Церера.png', 180), "base_size": 180, "positions": []}
}

selected_object = None
current_menu = "main"
menus = {}

input_active = False
input_text = ""
mass_prompt = "Введите массу объекта (в массах Земли):"
pending_object = None

def select_object(obj_name):
    global input_active, pending_object
    pending_object = obj_name
    input_active = True

def create_menus():
    global menus
    menus["main"] = [
        {"text": "Планеты", "submenu": "planets", "icon": planet_icon},
        {"text": "Звезды", "submenu": "stars", "icon": star_icon},
        {"text": "Астероид", "submenu": "asteroid", "icon": asteroid_icon},
    ]

    menus["planets"] = [
        {"text": "Меркурий", "action": lambda: select_object("mercury")},
        {"text": "Венера", "action": lambda: select_object("venus")},
        {"text": "Земля", "action": lambda: select_object("earth")},
        {"text": "Марс", "action": lambda: select_object("mars")},
        {"text": "Юпитер", "action": lambda: select_object("jupiter")},
        {"text": "Сатурн", "action": lambda: select_object("saturn")},
        {"text": "Уран", "action": lambda: select_object("uranium")},
        {"text": "Нептун", "action": lambda: select_object("neptune")},
    ]

    menus["stars"] = [
        {"text": "Сириус", "action": lambda: select_object("sirius")},
        {"text": "Канопус", "action": lambda: select_object("canopus")},
        {"text": "Арктур", "action": lambda: select_object("arcturus")},
        {"text": "Вега", "action": lambda: select_object("vega")},
        {"text": "Альдебаран", "action": lambda: select_object("aldebaran")},
    ]

    menus["asteroid"] = [
        {"text": "16 Психея", "action": lambda: select_object("psyche")},
        {"text": "Диморф", "action": lambda: select_object("dimorph")},
        {"text": "Бенну", "action": lambda: select_object("bennu")},
        {"text": "Рюгу", "action": lambda: select_object("ryugu")},
        {"text": "Церера", "action": lambda: select_object("ceres")},
    ]

create_menus()

def draw_text_or_icon(item, rect, hover=False):
    if "icon" in item:
        icon_surf = item["icon"]
        if icon_surf == star_icon:
            bg_rect = rect.inflate(25, 20)
            pygame.draw.rect(screen, WHITE, bg_rect, border_radius=8)
        icon_rect = icon_surf.get_rect(center=rect.center)
        screen.blit(icon_surf, icon_rect)
    else:
        color = BLACK
        bg_color = LIGHT_BLUE if hover else WHITE
        pygame.draw.rect(screen, bg_color, rect, border_radius=4)
        text_surf = font.render(item["text"], True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

def handle_menu_click(pos):
    global current_menu
    for item in menus[current_menu]:
        if "rect" in item and item["rect"] and item["rect"].collidepoint(pos):
            if "submenu" in item:
                current_menu = item["submenu"]
                return
            elif "action" in item:
                item["action"]()
                return
    if current_menu != "main":
        current_menu = "main"

def place_object_with_mass(pos, obj_name, mass):
    try:
        mass_value = float(mass)
        mass_value = max(0.1, min(mass_value, 100))
        size_multiplier = 0.8 + (mass_value ** 0.5) / 8
        obj_data = celestial_objects[obj_name]
        base_size = obj_data["base_size"]
        new_size = int(base_size * size_multiplier * SCALE_FACTOR)
        original_image = obj_data["image"]
        scaled_image = pygame.transform.smoothscale(original_image, (new_size, new_size))
        if scaled_image.get_width() != scaled_image.get_height():
            size = max(scaled_image.get_width(), scaled_image.get_height())
            square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            square_surface.fill((0, 0, 0, 0))
            x_offset = (size - scaled_image.get_width()) // 2
            y_offset = (size - scaled_image.get_height()) // 2
            square_surface.blit(scaled_image, (x_offset, y_offset))
            scaled_image = make_circular_surface(square_surface)
        else:
            scaled_image = make_circular_surface(scaled_image)

        obj_data["positions"].append({
            "pos": pos,
            "image": scaled_image,
            "mass": mass_value,
            "original_size": base_size,
            "size_multiplier": size_multiplier
        })
    except ValueError:
        print("Некорректное значение массы")

def delete_object_at_pos(pos):
    for obj_name, obj_data in celestial_objects.items():
        for i, placed_obj in enumerate(obj_data["positions"]):
            obj_rect = placed_obj["image"].get_rect(center=placed_obj["pos"])
            if obj_rect.collidepoint(pos):
                obj_data["positions"].pop(i)
                return True
    return False

def scale_all_objects(factor):
    global SCALE_FACTOR, scaled_frames, gif_frames
    SCALE_FACTOR *= factor
    SCALE_FACTOR = max(0.2, min(SCALE_FACTOR, 2.0))
    scaled_frames = []
    for frame in gif_frames:
        scaled_surface = pygame.transform.smoothscale(
            frame,
            (int(frame.get_width() * SCALE_FACTOR), int(frame.get_height() * SCALE_FACTOR)),
        )
        scaled_frames.append(scaled_surface)
    for obj_name, obj_data in celestial_objects.items():
        for placed_obj in obj_data["positions"]:
            new_size = int(placed_obj["original_size"] * placed_obj["size_multiplier"] * SCALE_FACTOR)
            original_image = obj_data["image"]
            scaled_image = pygame.transform.smoothscale(original_image, (new_size, new_size))
            if scaled_image.get_width() != scaled_image.get_height():
                size = max(scaled_image.get_width(), scaled_image.get_height())
                square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                square_surface.fill((0, 0, 0, 0))
                x_offset = (size - scaled_image.get_width()) // 2
                y_offset = (size - scaled_image.get_height()) // 2
                square_surface.blit(scaled_image, (x_offset, y_offset))
                placed_obj["image"] = make_circular_surface(square_surface)
            else:
                placed_obj["image"] = make_circular_surface(scaled_image)

running = True
while running:
    screen.blit(background, (0, 0))
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            current_width, current_height = event.w, event.h
            screen = pygame.display.set_mode((current_width, current_height), pygame.RESIZABLE)
            background = pygame.transform.scale(background_original, (current_width, current_height))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if event.unicode.isdigit() or event.unicode == '.':
                        input_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            plus_rect = pygame.Rect(current_width // 2 - button_width - 20, current_height - 80, button_width, button_height)
            minus_rect = pygame.Rect(current_width // 2 + 20, current_height - 80, button_width, button_height)

            if event.button == 1:
                if plus_rect.collidepoint(pos):
                    scale_all_objects(1.1)
                    continue
                elif minus_rect.collidepoint(pos):
                    scale_all_objects(0.9)
                    continue
                menu_y = 10
                menu_width = 60
                menu_height = 30
                main_rects = [
                    pygame.Rect(10, menu_y, menu_width, menu_height),
                    pygame.Rect(10 + menu_width + 10, menu_y, menu_width, menu_height),
                    pygame.Rect(10 + 2*(menu_width + 10), menu_y, menu_width, menu_height)
                ]
                clicked_on_menu = False
                for i, item in enumerate(menus["main"]):
                    item["rect"] = main_rects[i]
                    if item["rect"].collidepoint(pos):
                        clicked_on_menu = True
                        break

                if not clicked_on_menu and current_menu != "main":
                    y_offset = 40
                    menu_item_height = 30
                    for item in menus[current_menu]:
                        item["rect"] = pygame.Rect(10, y_offset, 190, menu_item_height)
                        if item["rect"].collidepoint(pos):
                            clicked_on_menu = True
                            break
                        y_offset += menu_item_height + 5

                handle_menu_click(pos)
                if not clicked_on_menu and not input_active and pending_object and pos[1] > 80:
                    if input_text:
                        place_object_with_mass(pos, pending_object, input_text)
                    pending_object = None
                    input_text = ""

            elif event.button == 3:
                clicked_on_ui = False
                if plus_rect.collidepoint(pos) or minus_rect.collidepoint(pos):
                    clicked_on_ui = True

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
                        clicked_on_ui = True
                        break

                if not clicked_on_ui and current_menu != "main":
                    y_offset = 40
                    menu_item_height = 30
                    for item in menus[current_menu]:
                        item["rect"] = pygame.Rect(10, y_offset, 190, menu_item_height)
                        if item["rect"].collidepoint(pos):
                            clicked_on_ui = True
                            break
                        y_offset += menu_item_height + 5

                if not clicked_on_ui and pos[1] > 80:
                    if delete_object_at_pos(pos):
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
        hover = item["rect"].collidepoint(mouse_pos)
        draw_text_or_icon(item, item["rect"], hover)
    if current_menu != "main":
        y_offset = 40
        menu_item_height = 30
        for item in menus[current_menu]:
            item["rect"] = pygame.Rect(10, y_offset, 190, menu_item_height)
            hover = item["rect"].collidepoint(mouse_pos)
            draw_text_or_icon(item, item["rect"], hover)
            y_offset += menu_item_height + 5
    for obj_name, obj_data in celestial_objects.items():
        for placed_obj in obj_data["positions"]:
            img_rect = placed_obj["image"].get_rect(center=placed_obj["pos"])
            screen.blit(placed_obj["image"], img_rect)
    now = pygame.time.get_ticks()
    if now - last_update > frame_delay:
        current_frame = (current_frame + 1) % len(scaled_frames)
        last_update = now
    frame = scaled_frames[current_frame]
    x = (current_width - frame.get_width()) // 2
    y = (current_height - frame.get_height()) // 2
    screen.blit(frame, (x, y))

    if input_active:
        s = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        mass_input_rect = pygame.Rect(current_width // 2 - 150, current_height // 2 - 50, 300, 50)
        pygame.draw.rect(screen, WHITE, mass_input_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, mass_input_rect, 2, border_radius=10)
        prompt_surf = font.render(mass_prompt, True, YELLOW)
        prompt_rect = prompt_surf.get_rect(center=(current_width // 2, current_height // 2 - 80))
        prompt_shadow = font.render(mass_prompt, True, BLACK)
        shadow_rect = prompt_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        screen.blit(prompt_shadow, shadow_rect)
        screen.blit(prompt_surf, prompt_rect)

        text_surf = font.render(input_text, True, BLACK)
        text_rect = text_surf.get_rect(center=mass_input_rect.center)
        screen.blit(text_surf, text_rect)
        inst_surf = small_font.render("Нажмите Enter для подтверждения", True, YELLOW)
        inst_rect = inst_surf.get_rect(center=(current_width // 2, current_height // 2 + 30))
        inst_shadow = small_font.render("Нажмите Enter для подтверждения", True, BLACK)
        shadow_rect = inst_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        screen.blit(inst_shadow, shadow_rect)
        screen.blit(inst_surf, inst_rect)

    def draw_button(rect, label, tooltip=""):
        color = hover_color if rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, color, rect, border_radius=5)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        if tooltip and rect.collidepoint(mouse_pos):
            tooltip_surf = small_font.render(tooltip, True, WHITE)
            tooltip_rect = tooltip_surf.get_rect(midbottom=(rect.centerx, rect.top - 5))
            pygame.draw.rect(screen, BLACK, tooltip_rect.inflate(10, 5), border_radius=3)
            screen.blit(tooltip_surf, tooltip_rect)

    plus_rect = pygame.Rect(current_width // 2 - button_width - 20, current_height - 80, button_width, button_height)
    minus_rect = pygame.Rect(current_width // 2 + 20, current_height - 80, button_width, button_height)
    draw_button(plus_rect, "+")
    draw_button(minus_rect, "-")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()