import pygame

# Initialize Pygame
pygame.init()

# Initialize Pygame mixer
pygame.mixer.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_WIDTH, GRID_HEIGHT = 3000, 2250
TILE_WIDTH, TILE_HEIGHT = 40, 30
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = 400, 300
CAMERA_SPEED = 0.1
GRID_FADE_SPEED = 10

# Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("City Simulator")
clock = pygame.time.Clock()

# Load Assets
def load_image(path, size=None):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size) if size else image


# Font for FPS
font = pygame.font.SysFont("Courier", 20)


def load_image(path, size=None):
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size) if size else image
    except pygame.error as e:
        print(f"Failed to load image at {path}: {e}")
        return pygame.Surface((10, 10), pygame.SRCALPHA)  # Placeholder

# Load Sounds
def load_sound(path):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(0.5)  # Set volume to 50%
        return sound
    except pygame.error as e:
        print(f"Failed to load sound at {path}: {e}")
        return None

sounds = {
    "place_building": load_sound("assets/sound/ui/sfx_place.wav"),
    "remove_building": load_sound("assets/sound/ui/sfx_demolish.wav"),
    "place_road": load_sound("assets/sound/ui/sfx_roadext.wav"),
    "remove_road": load_sound("assets/sound/ui/sfx_demolishr.wav")
}

# Preload all assets into dictionaries
assets = {
    "background": load_image("assets/images/misc/background.png"),
    "grid": load_image("assets/images/misc/grid_tiles.png"),
    "ui": load_image("assets/images/ui/ui_bg.png", (SCREEN_WIDTH, int(SCREEN_HEIGHT * 0.15))),
    "buildings": {
        'lshape': [
            {'footprint': [[1, 1], [0,1]], 'sprite': load_image("assets/images/buildings/building2_0.png")},
            {'footprint': [[1, 1], [1,0]], 'sprite': load_image("assets/images/buildings/building2_90.png")},
            {'footprint': [[1, 0], [1,1]], 'sprite': load_image("assets/images/buildings/building2_180.png")},
            {'footprint': [[0, 1], [1,1]], 'sprite': load_image("assets/images/buildings/building2_270.png")},
        ],
        '11seven': [
            {'footprint': [[1, 1], [1,1]], 'sprite': load_image("assets/images/buildings/com_11seven_0.png")},
            {'footprint': [[1, 1], [1,1]], 'sprite': load_image("assets/images/buildings/com_11seven_90.png")},
            {'footprint': [[1, 1], [1,1]], 'sprite': load_image("assets/images/buildings/com_11seven_180.png")},
            {'footprint': [[1, 1], [1,1]], 'sprite': load_image("assets/images/buildings/com_11seven_270.png")},
        ],
        'asphalt_straight': [
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_straight_0-180.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_straight_90-270.png")},
        ],
        'asphalt_3way': [
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_3way_0.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_3way_90.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_3way_180.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_3way_270.png")},
        ],
        'asphalt_4way': [
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_4way_0-90-180-270.png")},
        ],
        'asphalt_curve': [
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_curve_0.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_curve_90.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_curve_180.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_curve_270.png")},
        ],
        'asphalt_uturn': [
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_uturn_0.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_uturn_90.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_uturn_180.png")},
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_uturn_270.png")},
        ],
        'asphalt_dot': [
            {'footprint': [[1]], 'sprite': load_image("assets/images/roads/asphalt_dot_0-90-180-270.png")},
        ],
    }
}
# Building Data
building_variants = assets["buildings"]

# Game State
building_list = []
collision_grid = [[False for _ in range(GRID_HEIGHT // TILE_HEIGHT)] for _ in range(GRID_WIDTH // TILE_WIDTH)]
current_building_type = '11seven'
rotation = 0
camera_x, camera_y, camera_target_x, camera_target_y = 0, 0, 0, 0
grid_alpha = 255
fade_direction = 0
key_pressed = False










# Font Setup
info_font = pygame.font.Font(None, 15)
name_font = pygame.font.Font(None, 24)
desc_font = pygame.font.Font(None, 15)
counter_font = pygame.font.Font(None, 18)
small_font = pygame.font.Font(None, 14)

background_image = assets["background"]
grid_image = assets["grid"]
ui_image = assets["ui"]

def is_road_tile(x, y):
    return any(
        b[0] == x and b[1] == y and b[2] == [[1]]
        for b in building_list
    )

def get_road_sprite(x, y):
    # Check neighboring tiles
    neighbors = {
        'up': y > 0 and collision_grid[x][y - 1] and is_road_tile(x, y - 1),
        'down': y < len(collision_grid[0]) - 1 and collision_grid[x][y + 1] and is_road_tile(x, y + 1),
        'left': x > 0 and collision_grid[x - 1][y] and is_road_tile(x - 1, y),
        'right': x < len(collision_grid) - 1 and collision_grid[x + 1][y] and is_road_tile(x + 1, y)
    }

    # Determine the appropriate sprite based on neighbors
    if neighbors['up'] and neighbors['down'] and neighbors['left'] and neighbors['right']:
        return assets['buildings']['asphalt_4way'][0]['sprite']
    elif neighbors['right'] and neighbors['down'] and neighbors['left']:
        return assets['buildings']['asphalt_3way'][0]['sprite']
    elif neighbors['up'] and neighbors['down'] and neighbors['left']:
        return assets['buildings']['asphalt_3way'][1]['sprite']
    elif neighbors['up'] and neighbors['left'] and neighbors['right']:
        return assets['buildings']['asphalt_3way'][2]['sprite']
    elif neighbors['down'] and neighbors['up'] and neighbors['right']:
        return assets['buildings']['asphalt_3way'][3]['sprite']
    elif neighbors['up'] and neighbors['down']:
        return assets['buildings']['asphalt_straight'][0]['sprite']
    elif neighbors['left'] and neighbors['right']:
        return assets['buildings']['asphalt_straight'][1]['sprite']
    elif neighbors['up'] and neighbors['right']:
        return assets['buildings']['asphalt_curve'][2]['sprite']
    elif neighbors['up'] and neighbors['left']:
        return assets['buildings']['asphalt_curve'][1]['sprite']
    elif neighbors['down'] and neighbors['right']:
        return assets['buildings']['asphalt_curve'][3]['sprite']
    elif neighbors['down'] and neighbors['left']:
        return assets['buildings']['asphalt_curve'][0]['sprite']
    elif neighbors['up']:
        return assets['buildings']['asphalt_uturn'][2]['sprite']
    elif neighbors['down']:
        return assets['buildings']['asphalt_uturn'][0]['sprite']
    elif neighbors['left']:
        return assets['buildings']['asphalt_uturn'][1]['sprite']
    elif neighbors['right']:
        return assets['buildings']['asphalt_uturn'][3]['sprite']
    else:
        return assets['buildings']['asphalt_dot'][0]['sprite']

def place_road(x, y):
    if current_tool != TOOL_ROAD:
        return
    grid_x, grid_y = mouse_to_grid_coords(x, y)
    if not is_cell_occupied(grid_x, grid_y, [[1]]):
        collision_grid[grid_x][grid_y] = True
        sprite = get_road_sprite(grid_x, grid_y)
        building_list.append((grid_x, grid_y, [[1]], sprite, 0))
        update_neighboring_road_sprites(grid_x, grid_y)
        if sounds["place_road"]:
            sounds["place_road"].play()

def remove_road(x, y):
    if current_tool != TOOL_ROAD:
        return
    grid_x, grid_y = mouse_to_grid_coords(x, y)
    for b in building_list[:]:  # Use a copy to safely remove items while iterating
        if b[0] == grid_x and b[1] == grid_y and b[2] == [[1]]:  # Ensure it's a road tile
            building_list.remove(b)
            free_cells(b[0], b[1], b[2])
            collision_grid[grid_x][grid_y] = False
            update_neighboring_road_sprites(grid_x, grid_y)
            if sounds["remove_road"]:
                sounds["remove_road"].play()
            break

def update_neighboring_road_sprites(x, y):
    neighbors = [
        (x, y),
        (x, y - 1),
        (x, y + 1),
        (x - 1, y),
        (x + 1, y)
    ]
    for nx, ny in neighbors:
        if 0 <= nx < len(collision_grid) and 0 <= ny < len(collision_grid[0]) and collision_grid[nx][ny]:
            # Check if the neighboring cell is a road tile
            if is_road_tile(nx, ny):
                sprite = get_road_sprite(nx, ny)
                for i, (bx, by, footprint, _, rotation) in enumerate(building_list):
                    if bx == nx and by == ny and footprint == [[1]]:
                        building_list[i] = (bx, by, footprint, sprite, rotation)
                        break

# Helper Functions
def mouse_to_grid_coords(x, y):
    return int((x + camera_x) // TILE_WIDTH), int((y + camera_y) // TILE_HEIGHT)

def rotate_footprint(footprint):
    return list(zip(*footprint[::-1]))

def is_cell_occupied(x, y, footprint):
    for dx in range(len(footprint)):
        for dy in range(len(footprint[dx])):
            if x + dx >= len(collision_grid) or y + dy >= len(collision_grid[0]) or (footprint[dx][dy] == 1 and collision_grid[x + dx][y + dy]):
                return True
    return False

def mark_cells_occupied(x, y, footprint):
    for dx in range(len(footprint)):
        for dy in range(len(footprint[dx])):
            if footprint[dx][dy] == 1:
                collision_grid[x + dx][y + dy] = True

def free_cells(x, y, footprint):
    for dx in range(len(footprint)):
        for dy in range(len(footprint[dx])):
            if footprint[dx][dy] == 1:
                collision_grid[x + dx][y + dy] = False

def apply_tint(sprite, color):
    tinted = sprite.copy()
    tint_surface = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
    tint_surface.fill(color)
    tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

def render_buildings():
    # Sort buildings by their 'y' position (tile row) to render from front to back
    sorted_buildings = sorted(building_list, key=lambda b: b[1])  # Sort by 'y' position
    
    for x, y, footprint, sprite, _ in sorted_buildings:
        # Calculate screen position
        screen_x, screen_y = x * TILE_WIDTH - camera_x - 40, y * TILE_HEIGHT - camera_y - 30
        # Check if the building is within the visible screen area
        if -120 < screen_x < SCREEN_WIDTH and -120 < screen_y < SCREEN_HEIGHT:
            screen.blit(sprite, (screen_x, screen_y))

def render_ghost_building():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    grid_x, grid_y = mouse_to_grid_coords(mouse_x, mouse_y)
    
    if current_tool == TOOL_BUILDING:
        variant = building_variants[current_building_type][rotation % len(building_variants[current_building_type])]
        sprite = variant['sprite']
        footprint = variant['footprint']
    elif current_tool == TOOL_ROAD:
        sprite = assets['buildings']['asphalt_dot'][0]['sprite']
        footprint = [[1]]
    
    if is_cell_occupied(grid_x, grid_y, footprint):
        tint_color = (255, 0, 0, 128)  # Red tint for occupied cells
    else:
        tint_color = (0, 255, 0, 128)  # Green tint for free cells
    
    screen_x, screen_y = grid_x * TILE_WIDTH - camera_x - 40, grid_y * TILE_HEIGHT - camera_y - 30
    if -90 < screen_x < SCREEN_WIDTH and -90 < screen_y < SCREEN_HEIGHT:
        tinted_sprite = apply_tint(sprite, tint_color)
        screen.blit(tinted_sprite, (screen_x, screen_y))

# Pre-render the grid
def create_grid_surface(grid_image, grid_width, grid_height, tile_width, tile_height):
    grid_surface = pygame.Surface((grid_width, grid_height), pygame.SRCALPHA)
    for x in range(0, grid_width, tile_width):
        for y in range(0, grid_height, tile_height):
            grid_surface.blit(grid_image, (x, y))
    return grid_surface

# Generate the pre-rendered grid
grid_surface = create_grid_surface(grid_image, GRID_WIDTH, GRID_HEIGHT, TILE_WIDTH, TILE_HEIGHT)

# Function to render the grid
def render_grid(camera_x, camera_y, screen, grid_surface, grid_alpha):
    if grid_alpha == 0:  # Skip rendering when the grid is fully transparent
        return
    visible_area = pygame.Rect(camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT)
    grid_clip = grid_surface.subsurface(visible_area)
    grid_clip.set_alpha(grid_alpha)
    screen.blit(grid_clip, (0, 0))


def remove_road(x, y):
    if current_tool != TOOL_ROAD:
        return
    grid_x, grid_y = mouse_to_grid_coords(x, y)
    for b in building_list[:]:  # Use a copy to safely remove items while iterating
        if b[0] == grid_x and b[1] == grid_y and b[2] == [[1]]:  # Ensure it's a road tile
            building_list.remove(b)
            free_cells(b[0], b[1], b[2])
            collision_grid[grid_x][grid_y] = False
            update_neighboring_road_sprites(grid_x, grid_y)
            if sounds["remove_building"]:
                sounds["remove_building"].play()
            break

def remove_building(x, y):
    if current_tool != TOOL_BUILDING:
        return
    grid_x, grid_y = mouse_to_grid_coords(x, y)
    for b in building_list[:]:  # Use a copy to safely remove items while iterating
        if b[0] <= grid_x < b[0] + len(b[2]) and b[1] <= grid_y < b[1] + len(b[2][0]) and b[2] != [[1]]:  # Ensure it's a building
            building_list.remove(b)
            free_cells(b[0], b[1], b[2])
            if sounds["remove_building"]:
                sounds["remove_building"].play()
            break


 

TOOL_ROAD = 'road'
TOOL_BUILDING = 'building'

# Initial tool
current_tool = TOOL_BUILDING

# Track mouse button state
left_mouse_button_down = False
right_mouse_button_down = False

# Main Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type in (pygame.QUIT, pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_to_grid_coords(mouse_x, mouse_y)
            if current_tool == TOOL_BUILDING:
                variant = building_variants[current_building_type][rotation % len(building_variants[current_building_type])]
                if event.button == 1 and mouse_y < SCREEN_HEIGHT - ui_image.get_height():  # Left click for placement
                    if not is_cell_occupied(grid_x, grid_y, variant['footprint']):
                        building_list.append((grid_x, grid_y, variant['footprint'], variant['sprite'], rotation))
                        mark_cells_occupied(grid_x, grid_y, variant['footprint'])
                        if sounds["place_building"]:
                            sounds["place_building"].play()
                elif event.button == 3:  # Right click for removal
                    right_mouse_button_down = True
                    remove_building(mouse_x, mouse_y)
            elif current_tool == TOOL_ROAD:
                if event.button == 1 and mouse_y < SCREEN_HEIGHT - ui_image.get_height():  # Left click for placement
                    left_mouse_button_down = True
                    place_road(mouse_x, mouse_y)
                elif event.button == 3:  # Right click for removal
                    right_mouse_button_down = True
                    remove_road(mouse_x, mouse_y)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                left_mouse_button_down = False
            elif event.button == 3:
                right_mouse_button_down = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                rotation = (rotation + 1) % 4
            elif event.key == pygame.K_b:
                current_tool = TOOL_BUILDING
            elif event.key == pygame.K_t:
                current_tool = TOOL_ROAD

    if current_tool == TOOL_ROAD:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if left_mouse_button_down:
            place_road(mouse_x, mouse_y)
        elif right_mouse_button_down:
            remove_road(mouse_x, mouse_y)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_g] and not key_pressed:
        fade_direction = 1 if grid_alpha == 0 else -1
        key_pressed = True
    elif not keys[pygame.K_g]:
        key_pressed = False

    if fade_direction:
        grid_alpha = max(0, min(255, grid_alpha + fade_direction * GRID_FADE_SPEED))
        fade_direction = 0 if grid_alpha in {0, 255} else fade_direction

    # Camera Movement
    camera_target_x += (keys[pygame.K_d] - keys[pygame.K_a]) * 10
    camera_target_y += (keys[pygame.K_s] - keys[pygame.K_w]) * 10
    camera_target_x = max(0, min(camera_target_x, GRID_WIDTH - SCREEN_WIDTH))
    camera_target_y = max(0, min(camera_target_y, GRID_HEIGHT - SCREEN_HEIGHT))
    camera_x += (camera_target_x - camera_x) * CAMERA_SPEED
    camera_y += (camera_target_y - camera_y) * CAMERA_SPEED

    # Drawing
    screen.fill((0, 0, 0))
    for x in range(-1, (SCREEN_WIDTH // BACKGROUND_WIDTH) + 2):
        for y in range(-1, (SCREEN_HEIGHT // BACKGROUND_HEIGHT) + 2):
            screen.blit(background_image, (x * BACKGROUND_WIDTH - camera_x % BACKGROUND_WIDTH, 
                                           y * BACKGROUND_HEIGHT - camera_y % BACKGROUND_HEIGHT))

    render_buildings()
    render_ghost_building()

    render_grid(camera_x, camera_y, screen, grid_surface, grid_alpha)

    # FPS
    fps_text = font.render(f"{int(clock.get_fps())} fps", True, (0, 255, 0))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()