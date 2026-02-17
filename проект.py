import pygame
from PIL import Image

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

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 150, 255)
LIGHT_BLUE = (150, 200, 255)

font = pygame.font.SysFont(None, 36)
background = pygame.image.load('cosmos.jpg').convert()


GIF_PATH = "sun.gif"
pil_frames = extract_gif_frames(GIF_PATH)
gif_frames = load_frames_as_surfaces(pil_frames)

SUN_SCALE_FACTOR = 0.5
scaled_frames = []
for frame in gif_frames:
    scaled_surface = pygame.transform.smoothscale(frame, (int(frame.get_width() * SUN_SCALE_FACTOR), int(frame.get_height() * SUN_SCALE_FACTOR)))
    scaled_frames.append(scaled_surface)

button_width, button_height = 100, 50
plus_button = pygame.Rect(WIDTH // 2 - button_width - 20, HEIGHT - 100, button_width, button_height)
minus_button = pygame.Rect(WIDTH // 2 + 20, HEIGHT - 100, button_width, button_height)

button_color = (50, 50, 50)
hover_color = (100, 100, 100)

current_frame = 0
frame_delay = 100
last_update = pygame.time.get_ticks()

planet_icon = pygame.image.load('значок_планеты.jpg').convert_alpha()
planet_icon = pygame.transform.scale(planet_icon, (50, 50))

star_icon = pygame.image.load('значок_звезды.webp').convert_alpha()
star_icon = pygame.transform.scale(star_icon, (50, 50))

asteroid_icon = pygame.image.load('значок_астероида.webp').convert_alpha()
asteroid_icon = pygame.transform.scale(asteroid_icon, (50, 50))

earth_image = pygame.image.load('Земля.png').convert_alpha()
earth_image = pygame.transform.scale(earth_image, (120, 120))

mercury_image = pygame.image.load('Меркурий.png').convert_alpha()
mercury_image = pygame.transform.scale(mercury_image, (80, 80))

venus_image = pygame.image.load('Венера.png').convert_alpha()
venus_image = pygame.transform.scale(venus_image, (80, 80))

mars_image = pygame.image.load('Марс.png').convert_alpha()
mars_image = pygame.transform.scale(mars_image, (70, 70))

jupiter_image = pygame.image.load('Юпитер.png').convert_alpha()
jupiter_image = pygame.transform.scale(jupiter_image, (140, 140))

saturn_image = pygame.image.load('Сатурн.png').convert_alpha()
saturn_image = pygame.transform.scale(saturn_image, (180, 180))

uranium_image = pygame.image.load('Уран.png').convert_alpha()
uranium_image = pygame.transform.scale(uranium_image, (170, 170))

neptune_image = pygame.image.load('Нептун.png').convert_alpha()
neptune_image = pygame.transform.scale(neptune_image, (100, 100))

sirius_image = pygame.image.load('Сириус.png').convert_alpha()
sirius_image = pygame.transform.scale(sirius_image, (240, 160))

canopus_image = pygame.image.load('Канопус.png').convert_alpha()
canopus_image = pygame.transform.scale(canopus_image, (100, 100))

arcturus_image = pygame.image.load('Арктур.png').convert_alpha()
arcturus_image = pygame.transform.scale(arcturus_image, (100, 120))

vega_image = pygame.image.load('Вега.png').convert_alpha()
vega_image = pygame.transform.scale(vega_image, (120, 120))

aldebaran_image = pygame.image.load('Альдебаран.png').convert_alpha()
aldebaran_image = pygame.transform.scale(aldebaran_image, (100, 120))

psyche_image = pygame.image.load('16 Психея.png').convert_alpha()
psyche_image = pygame.transform.scale(psyche_image, (100, 100))

dimorph_image = pygame.image.load('Диморф.png').convert_alpha()
dimorph_image = pygame.transform.scale(dimorph_image, (100, 100))

bennu_image = pygame.image.load('Бенну.png').convert_alpha()
bennu_image = pygame.transform.scale(bennu_image, (100, 100))

ryugu_image = pygame.image.load('Рюгу.png').convert_alpha()
ryugu_image = pygame.transform.scale(ryugu_image, (100, 100))

ceres_image = pygame.image.load('Церера.png').convert_alpha()
ceres_image = pygame.transform.scale(ceres_image, (100, 100))

selected_image = None

earth_positions = []
mercury_positions = []
venus_positions = []
mars_positions = []
jupiter_positions = []
saturn_positions = []
uranium_positions = []
neptune_positions = []

sirius_positions = []
canopus_positions = []
arcturus_positions = []
vega_positions = []
aldebaran_positions = []

psyche_positions = []
dimorph_positions = []
bennu_positions = []
ryugu_positions = []
ceres_positions = []


current_menu = "main"
menus = {}

def exit_app():
    pygame.quit()
    quit()

def select_earth():
    global selected_image
    selected_image = earth_image

def select_mercury():
    global selected_image
    selected_image = mercury_image

def select_venus():
    global selected_image
    selected_image = venus_image

def select_mars():
    global selected_image
    selected_image = mars_image

def select_jupiter():
    global selected_image
    selected_image = jupiter_image

def select_saturn():
    global selected_image
    selected_image = saturn_image

def select_uranium():
    global selected_image
    selected_image = uranium_image

def select_neptune():
    global selected_image
    selected_image = neptune_image

def select_sirius():
    global selected_image
    selected_image = sirius_image

def select_canopus():
    global selected_image
    selected_image = canopus_image

def select_arcturus():
    global selected_image
    selected_image = arcturus_image

def select_vega():
    global selected_image
    selected_image = vega_image

def select_aldebaran():
    global selected_image
    selected_image = aldebaran_image

def select_psyche():
    global selected_image
    selected_image = psyche_image

def select_dimorph():
    global selected_image
    selected_image = dimorph_image

def select_bennu():
    global selected_image
    selected_image = bennu_image

def select_ryugu():
    global selected_image
    selected_image = ryugu_image

def select_ceres():
    global selected_image
    selected_image = ceres_image

def create_menus():
    global menus
    menus["main"] = [
        {"text": "Планеты", "submenu": "planets", "rect": pygame.Rect(10, 10, 60, 30), "icon": planet_icon},
        {"text": "Звезды", "submenu": "stars", "rect": pygame.Rect(70, 10, 60, 30), "icon": star_icon},
        {"text": "Астероид", "submenu": "asteroid", "rect": pygame.Rect(130, 10, 60, 30), "icon": asteroid_icon},
    ]

    menus["planets"] = [
        {"text": "Меркурий", "action": select_mercury},
        {"text": "Венера", "action": select_venus},
        {"text": "Земля", "action": select_earth},
        {"text": "Марс", "action": select_mars},
        {"text": "Юпитер", "action": select_jupiter},
        {"text": "Сатурн", "action": select_saturn},
        {"text": "Уран", "action": select_uranium},
        {"text": "Нептун", "action": select_neptune},
    ]

    menus["stars"] = [
        {"text": "Сириус", "action": select_sirius},
        {"text": "Канопус", "action": select_canopus},
        {"text": "Арктур", "action": select_arcturus},
        {"text": "Вега", "action": select_vega},
        {"text": "Альдебаран", "action": select_aldebaran},
    ]

    menus["asteroid"] = [
        {"text": "16 Психея", "action": select_psyche},
        {"text": "Диморф", "action": select_dimorph},
        {"text": "Бенну", "action": select_bennu},
        {"text": "Рюгу", "action": select_ryugu},
        {"text": "Церера", "action": select_ceres},
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

running = True
while running:
    screen.fill(BLACK)
    screen.blit(background, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if plus_button.collidepoint(pos):
                SUN_SCALE_FACTOR += 0.1
                scaled_frames = []
                for frame in gif_frames:
                    scaled_surface = pygame.transform.smoothscale(
                        frame,
                        (
                            int(frame.get_width() * SUN_SCALE_FACTOR),
                            int(frame.get_height() * SUN_SCALE_FACTOR),
                        ),
                    )
                    scaled_frames.append(scaled_surface)
            elif minus_button.collidepoint(pos):
                SUN_SCALE_FACTOR -= 0.1
                scaled_frames = []
                for frame in gif_frames:
                    scaled_surface = pygame.transform.smoothscale(
                        frame,
                        (
                            int(frame.get_width() * SUN_SCALE_FACTOR),
                            int(frame.get_height() * SUN_SCALE_FACTOR),
                        ),
                    )
                    scaled_frames.append(scaled_surface)

            clicked_on_menu = False
            for item in menus["main"]:
                if item["rect"].collidepoint(pos):
                    clicked_on_menu = True
                    break

            if not clicked_on_menu and current_menu != "main":
                for item in menus[current_menu]:
                    r = item.get("rect")
                    if r is not None and r.collidepoint(pos):
                        clicked_on_menu = True
                        break
            handle_menu_click(pos)

            if (
                selected_image == earth_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                earth_positions.append(pos)

            if (
                selected_image == mercury_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                mercury_positions.append(pos)

            if (
                selected_image == venus_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                venus_positions.append(pos)

            if (
                selected_image == mars_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                mars_positions.append(pos)

            if (
                selected_image == jupiter_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                jupiter_positions.append(pos)

            if (
                selected_image == saturn_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                saturn_positions.append(pos)

            if (
                selected_image == uranium_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                uranium_positions.append(pos)

            if (
                selected_image == neptune_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                neptune_positions.append(pos)

            if (
                selected_image == sirius_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                sirius_positions.append(pos)

            if (
                selected_image == canopus_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                canopus_positions.append(pos)

            if (
                selected_image == arcturus_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                arcturus_positions.append(pos)

            if (
                selected_image == vega_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                vega_positions.append(pos)

            if (
                selected_image == aldebaran_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                aldebaran_positions.append(pos)

            if (
                selected_image == psyche_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                psyche_positions.append(pos)

            if (
                selected_image == dimorph_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                dimorph_positions.append(pos)

            if (
                selected_image == bennu_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                bennu_positions.append(pos)

            if (
                selected_image == ryugu_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                ryugu_positions.append(pos)

            if (
                selected_image == ceres_image
                and pos[1] > 80
                and not clicked_on_menu
                and not plus_button.collidepoint(pos)
                and not minus_button.collidepoint(pos)
            ):
                ceres_positions.append(pos)

    for item in menus["main"]:
        hover = item["rect"].collidepoint(mouse_pos)
        draw_text_or_icon(item, item["rect"], hover)

    if current_menu != "main":
        y_offset = 40
        for item in menus[current_menu]:
            if item.get("type") == "separator":
                pygame.draw.line(screen, GRAY, (10, y_offset + 5), (200, y_offset + 5), 1)
                y_offset += 15
                continue

            menu_item_rect = pygame.Rect(10, y_offset, 190, 30)
            item["rect"] = menu_item_rect
            hover = menu_item_rect.collidepoint(mouse_pos)
            draw_text_or_icon(item, menu_item_rect, hover)
            y_offset += 30

    for pos in earth_positions:
        img_rect = earth_image.get_rect(center=pos)
        screen.blit(earth_image, img_rect)

    for pos in mercury_positions:
        img_rect = mercury_image.get_rect(center=pos)
        screen.blit(mercury_image, img_rect)

    for pos in venus_positions:
        img_rect = venus_image.get_rect(center=pos)
        screen.blit(venus_image, img_rect)

    for pos in mars_positions:
        img_rect = mars_image.get_rect(center=pos)
        screen.blit(mars_image, img_rect)

    for pos in jupiter_positions:
        img_rect = jupiter_image.get_rect(center=pos)
        screen.blit(jupiter_image, img_rect)

    for pos in saturn_positions:
        img_rect = saturn_image.get_rect(center=pos)
        screen.blit(saturn_image, img_rect)

    for pos in uranium_positions:
        img_rect = uranium_image.get_rect(center=pos)
        screen.blit(uranium_image, img_rect)

    for pos in neptune_positions:
        img_rect = neptune_image.get_rect(center=pos)
        screen.blit(neptune_image, img_rect)

    for pos in sirius_positions:
        img_rect = sirius_image.get_rect(center=pos)
        screen.blit(sirius_image, img_rect)

    for pos in canopus_positions:
        img_rect = canopus_image.get_rect(center=pos)
        screen.blit(canopus_image, img_rect)

    for pos in arcturus_positions:
        img_rect = arcturus_image.get_rect(center=pos)
        screen.blit(arcturus_image, img_rect)

    for pos in vega_positions:
        img_rect = vega_image.get_rect(center=pos)
        screen.blit(vega_image, img_rect)

    for pos in aldebaran_positions:
        img_rect = aldebaran_image.get_rect(center=pos)
        screen.blit(aldebaran_image, img_rect)

    for pos in psyche_positions:
        img_rect = psyche_image.get_rect(center=pos)
        screen.blit(psyche_image, img_rect)

    for pos in dimorph_positions:
        img_rect = dimorph_image.get_rect(center=pos)
        screen.blit(dimorph_image, img_rect)

    for pos in bennu_positions:
        img_rect = bennu_image.get_rect(center=pos)
        screen.blit(bennu_image, img_rect)

    for pos in ryugu_positions:
        img_rect = ryugu_image.get_rect(center=pos)
        screen.blit(ryugu_image, img_rect)

    for pos in ceres_positions:
        img_rect = ceres_image.get_rect(center=pos)
        screen.blit(ceres_image, img_rect)

    now = pygame.time.get_ticks()
    if now - last_update > frame_delay:
        current_frame = (current_frame + 1) % len(scaled_frames)
        last_update = now

    frame = scaled_frames[current_frame]
    x = (screen.get_width() - frame.get_width()) // 2
    y = (screen.get_height() - frame.get_height()) // 2
    screen.blit(frame, (x, y))

    def draw_button(rectangle, label):
        color = hover_color if rectangle.collidepoint(pygame.mouse.get_pos()) else button_color
        pygame.draw.rect(screen, color, rectangle)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=rectangle.center)
        screen.blit(text, text_rect)

    draw_button(plus_button, "+")
    draw_button(minus_button, "-")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()