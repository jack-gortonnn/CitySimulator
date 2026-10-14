import pygame, sys, os, time

# Initialisation (pyGame, changing active directories)

pygame.init()
pygame.mixer.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Constants (Resolution, grid sizes)

screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
GRID_SIZE, GRID_COLOR = 35, (0, 0, 0)
GRID_WIDTH, GRID_HEIGHT = WIDTH // GRID_SIZE, HEIGHT // GRID_SIZE

# Setup (Display, cursors, sounds, counters, timer, fonts and background)

pygame.display.set_caption("City Simulator")
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
cursor_x, cursor_y = 0, 0

sfx_music = pygame.mixer.Sound("assets/sfx_music.wav") 
sfx_place = pygame.mixer.Sound("assets/sfx_place.wav")
sfx_remove = pygame.mixer.Sound("assets/sfx_remove.wav")
sfx_rotate = pygame.mixer.Sound("assets/sfx_rotate.wav")
sfx_error = pygame.mixer.Sound("assets/sfx_error.wav")

sfx_music.set_volume(0.2)
sfx_place.set_volume(0.4)
sfx_remove.set_volume(0.3)
sfx_rotate.set_volume(0.8)
sfx_error.set_volume(0.05)

sfx_music.play(-1)

num_population = 0
num_maintenance = 0
num_revenue = 0
num_balance = 1500

money_timer = time.time()

font = pygame.font.Font(None, 20)
font_counters = pygame.font.Font(None, 24)
background_image = pygame.image.load("assets/texture_grass.png").convert()

# Building dict (Name, color, population, revenue, maintenance, cost, images)

BUILDING_TYPES = {
    "Straight": {
        "color": (90, 90, 95), "pop": 0, "rev": 0, "mai": 1, "cost": 10,
        "images": {"north": pygame.image.load("assets/road_strt_ns.png"), "south": pygame.image.load("assets/road_strt_ns.png"),
                   "east": pygame.image.load("assets/road_strt_ew.png"), "west": pygame.image.load("assets/road_strt_ew.png")},
    },
    "Crossing": {
        "color": (85, 85, 90), "pop": 0, "rev": 0, "mai": 3, "cost": 30,
        "images": {"north": pygame.image.load("assets/road_cros_ns.png"), "south": pygame.image.load("assets/road_cros_ns.png"),
                   "east": pygame.image.load("assets/road_cros_ew.png"), "west": pygame.image.load("assets/road_cros_ew.png")},
    },
    "U-Turn": {
        "color": (80, 80, 85), "pop": 0, "rev": 0, "mai": 1, "cost": 15,
        "images": {"north": pygame.image.load("assets/road_turn_n.png"), "south": pygame.image.load("assets/road_turn_s.png"),
                   "east": pygame.image.load("assets/road_turn_e.png"), "west": pygame.image.load("assets/road_turn_w.png")},
    },    
    "Curved": {
        "color": (75, 75, 80), "pop": 0, "rev": 0, "mai": 2, "cost": 20,
        "images": {"north": pygame.image.load("assets/road_curv_n.png"), "south": pygame.image.load("assets/road_curv_s.png"),
                   "east": pygame.image.load("assets/road_curv_e.png"), "west": pygame.image.load("assets/road_curv_w.png")},
    },
    "3-Way": {
        "color": (70, 70, 75), "pop": 0, "rev": 0, "mai": 3, "cost": 30,
        "images": {"north": pygame.image.load("assets/road_3way_n.png"), "south": pygame.image.load("assets/road_3way_s.png"),
                   "east": pygame.image.load("assets/road_3way_e.png"), "west": pygame.image.load("assets/road_3way_w.png")},
    },
    "4-Way": {
        "color": (65, 65, 70), "pop": 0, "rev": 0, "mai": 4, "cost": 40,
        "images": {"north": pygame.image.load("assets/road_4way_nsew.png"), "south": pygame.image.load("assets/road_4way_nsew.png"),
                   "east": pygame.image.load("assets/road_4way_nsew.png"), "west": pygame.image.load("assets/road_4way_nsew.png")},
    },
    "City Hall": {
        "color": (110, 70, 100), "pop": 0, "rev": 100, "mai": 0, "cost": 250,
        "images": {"north": pygame.image.load("assets/serv_hall_n.png"), "south": pygame.image.load("assets/serv_hall_s.png"),
                   "east": pygame.image.load("assets/serv_hall_e.png"), "west": pygame.image.load("assets/serv_hall_w.png")},
    },
    "Police Station": {
        "color": (105, 65, 95), "pop": 0, "rev": 70, "mai": 0, "cost": 150,
        "images": {"north": pygame.image.load("assets/serv_poli_n.png"), "south": pygame.image.load("assets/serv_poli_n.png"),
                   "east": pygame.image.load("assets/serv_poli_n.png"), "west": pygame.image.load("assets/serv_poli_n.png")},
    },
    "Fire Station": {
        "color": (100, 60, 90), "pop": 0, "rev": 70, "mai": 0, "cost": 150,
        "images": {"north": pygame.image.load("assets/serv_fire_n.png"), "south": pygame.image.load("assets/serv_fire_n.png"),
                   "east": pygame.image.load("assets/serv_fire_n.png"), "west": pygame.image.load("assets/serv_fire_n.png")},
    },
    "Hospital": {
        "color": (95, 55, 85), "pop": 0, "rev": 80, "mai":0, "cost": 200,
        "images": {"north": pygame.image.load("assets/serv_hosp_n.png"), "south": pygame.image.load("assets/serv_hosp_n.png"),
                   "east": pygame.image.load("assets/serv_hosp_n.png"), "west": pygame.image.load("assets/serv_hosp_n.png")},
    },
    "Caravan Park": {
        "color": (60, 120, 70), "pop": 10, "rev": 0, "mai": 0, "cost": 100,
        "images": {"north": pygame.image.load("assets/resi_1_n.png"), "south": pygame.image.load("assets/resi_1_s.png"),
                   "east": pygame.image.load("assets/resi_1_e.png"), "west": pygame.image.load("assets/resi_1_w.png")},
    },
    "Cozy Home": {
        "color": (55, 115, 65), "pop": 25, "rev": 0, "mai": 2, "cost": 250,
        "images": {"north": pygame.image.load("assets/resi_2_n.png"), "south": pygame.image.load("assets/resi_2_s.png"),
                   "east": pygame.image.load("assets/resi_2_e.png"), "west": pygame.image.load("assets/resi_2_w.png")},
    },
    "Urban Flats": {
        "color": (50, 110, 60), "pop": 50, "rev": 0, "mai": 5, "cost": 500,
        "images": {"north": pygame.image.load("assets/resi_3_n.png"), "south": pygame.image.load("assets/resi_3_s.png"),
                   "east": pygame.image.load("assets/resi_3_e.png"), "west": pygame.image.load("assets/resi_3_w.png")},
    },
    "Market Stall": {
        "color": (20, 80, 120), "pop": 0, "rev": 30, "mai": 1, "cost": 75,
        "images": {"north": pygame.image.load("assets/comm_stal_n.png"), "south": pygame.image.load("assets/comm_stal_n.png"),
                   "east": pygame.image.load("assets/comm_stal_n.png"), "west": pygame.image.load("assets/comm_stal_n.png")},
    },
    "Divine Diner": {
        "color": (15, 75, 115), "pop": 0, "rev": 150, "mai": 3, "cost": 300,
        "images": {"north": pygame.image.load("assets/comm_dine_n.png"), "south": pygame.image.load("assets/comm_dine_n.png"),
                   "east": pygame.image.load("assets/comm_dine_n.png"), "west": pygame.image.load("assets/comm_dine_n.png")},
    },
    "Pear Store": {
        "color": (10, 70, 110), "pop": 0, "rev": 1000, "mai": 10, "cost": 1000,
        "images": {"north": pygame.image.load("assets/comm_pear_n.png"), "south": pygame.image.load("assets/comm_pear_s.png"),
                   "east": pygame.image.load("assets/comm_pear_e.png"), "west": pygame.image.load("assets/comm_pear_w.png")},
    },
     "Grain Silo": {
        "color": (180, 120, 70), "pop": 0, "rev": 60, "mai": 20, "cost": 200,
        "images": {"north": pygame.image.load("assets/indu_silo_n.png"), "south": pygame.image.load("assets/indu_silo_s.png"),
                   "east": pygame.image.load("assets/indu_silo_e.png"), "west": pygame.image.load("assets/indu_silo_w.png")},
    },
    "Storage Depot": {
        "color": (175, 115, 65), "pop": 0, "rev": 120, "mai": 50, "cost": 500,
        "images": {"north": pygame.image.load("assets/indu_stor_ns.png"), "south": pygame.image.load("assets/indu_stor_ns.png"),
                   "east": pygame.image.load("assets/indu_stor_e.png"), "west": pygame.image.load("assets/indu_stor_w.png")},
    },
    "Fast Factory": {
        "color": (170, 110, 60), "pop": 0, "rev": 220, "mai": 100, "cost": 1000,
        "images": {"north": pygame.image.load("assets/indu_fact_n.png"), "south": pygame.image.load("assets/indu_fact_s.png"),
                   "east": pygame.image.load("assets/indu_fact_e.png"), "west": pygame.image.load("assets/indu_fact_w.png")},
    },
    "Row of Trees": {
        "color": (50, 100, 70), "pop": 0, "rev": 5, "mai": 0, "cost": 50,
        "images": {"north": pygame.image.load("assets/park_path_ns.png"), "south": pygame.image.load("assets/park_path_ns.png"),
                   "east": pygame.image.load("assets/park_path_ew.png"), "west": pygame.image.load("assets/park_path_ew.png")},
    },
    "Fountain Plaza": {
        "color": (45, 95, 65), "pop": 0, "rev": 15, "mai": 0, "cost": 250,
        "images": {"north": pygame.image.load("assets/park_tree_n.png"), "south": pygame.image.load("assets/park_tree_n.png"),
                   "east": pygame.image.load("assets/park_tree_n.png"), "west": pygame.image.load("assets/park_tree_n.png")},
    },
    "Basketball": {
        "color": (40, 90, 60), "pop": 0, "rev": 100, "mai": 1, "cost": 1500,
        "images": {"north": pygame.image.load("assets/park_bask_ns.png"), "south": pygame.image.load("assets/park_bask_ns.png"),
                   "east": pygame.image.load("assets/park_bask_ew.png"), "west": pygame.image.load("assets/park_bask_ew.png")},
    },
    "Golf Course": {
        "color": (35, 85, 55), "pop": 0, "rev": 300, "mai": 3, "cost": 3500,
        "images": {"north": pygame.image.load("assets/park_golf_n.png"), "south": pygame.image.load("assets/park_golf_s.png"),
                   "east": pygame.image.load("assets/park_golf_e.png"), "west": pygame.image.load("assets/park_golf_w.png")},
    },
    "Sky Tower": {
        "color": (30, 80, 50), "pop": 0, "rev": 2500, "mai": 50, "cost": 15000,
        "images": {"north": pygame.image.load("assets/park_towe_n.png"), "south": pygame.image.load("assets/park_towe_s.png"),
                   "east": pygame.image.load("assets/park_towe_e.png"), "west": pygame.image.load("assets/park_towe_w.png")},
    },
}

# Building setup (Active building, directions, and direction_index)

ACTIVE_BUILDING = "Straight"

DIRECTIONS = ["north", "east", "south", "west"]
direction_index = 0

show_selected_building = True
show_grid = True

# Grid initialization (both main and direction, plus collision grid)

grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
direction_grid = [["north" for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
grid_box = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
grid_box_rect = grid_box.get_rect(topleft=(160, 0))

# UI Buttons setup (UI Surface, list, plus positioning and colors)

button_list_surface = pygame.Surface((160, HEIGHT))
button_rects = []

for i, (building_type, color_data) in enumerate(BUILDING_TYPES.items()):
    button_rect = pygame.Rect(0, i * (HEIGHT // len(BUILDING_TYPES)), 180, (HEIGHT // len(BUILDING_TYPES)))
    button_rects.append((button_rect, building_type))

for button_rect, building_type in button_rects:
    pygame.draw.rect(button_list_surface, BUILDING_TYPES[building_type]["color"], button_rect)
    text = font.render(building_type, True, (255, 255, 255))
    text_rect = text.get_rect(center=button_rect.center)
    button_list_surface.blit(text, text_rect)

# Tint image functions (based on cost and availability)

def tint_image_red(image):
    red_tint = pygame.Surface(image.get_size())
    red_tint.fill((255, 100, 100))
    red_tint.set_alpha(100)
    tinted_image = image.copy()
    tinted_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_MULT)
    return tinted_image

def tint_image_green(image):
    red_tint = pygame.Surface(image.get_size())
    red_tint.fill((100, 255, 100))
    red_tint.set_alpha(100)
    tinted_image = image.copy()
    tinted_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_MULT)
    return tinted_image

# Main game loop

running = True

while running:

    # Updating the stats + counters every second

    size_x, size_y = 0, 0

    current_time = time.time()
    time_elapsed = current_time - money_timer

    if time_elapsed >= 1:
        num_balance += (num_revenue / 60)
        num_balance += (num_population / 60)
        num_balance -= (num_maintenance / 600)
        money_timer = current_time

    num_population = sum(BUILDING_TYPES[cell].get("pop", 0) for row in grid for cell in row if cell is not None)
    num_maintenance = sum(BUILDING_TYPES[cell].get("mai", 0) for row in grid for cell in row if cell is not None)
    num_revenue = sum(BUILDING_TYPES[cell].get("rev", 0) for row in grid for cell in row if cell is not None)    

    # Input handling

    for event in pygame.event.get():

        # Keyboard inputs

        if event.type == pygame.QUIT: # Close button quits pyGame
            running = False

        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_g: # G button toggles grid
                show_grid = not show_grid
            if event.key == pygame.K_r: # R button rotates current building
                direction_index = (direction_index + 1) % len(DIRECTIONS)
                sfx_rotate.play()
            if event.key == pygame.K_ESCAPE: # Esc button quits pyGame
                running = False

        # Mouse inputs

        if event.type == pygame.MOUSEBUTTONDOWN:

            # Finding active mouse position

            x, y = event.pos

            if event.button == 1:
                for button_rect, building_type in button_rects:

                    # If a button is left-clicked, change active building

                    if button_rect.collidepoint(x, y):
                        ACTIVE_BUILDING = building_type
                        selected_building = BUILDING_TYPES[ACTIVE_BUILDING]["images"][DIRECTIONS[direction_index]].copy()
                        selected_building.set_alpha(100)

                    # If grid is left-clicked, place active building and add any counters (if applicable)

                    elif grid_box_rect.collidepoint(x, y):
                        grid_x, grid_y = x // GRID_SIZE, y // GRID_SIZE
                        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                            if grid[grid_y][grid_x] is None:
                                if building_data.get("cost") <= num_balance:
                                    grid[grid_y][grid_x] = ACTIVE_BUILDING
                                    direction_grid[grid_y][grid_x] = DIRECTIONS[direction_index]
                                    building_data = BUILDING_TYPES[ACTIVE_BUILDING]
                                    num_population += building_data.get("pop", 0)
                                    num_maintenance += building_data.get("mai", 0)
                                    num_revenue += building_data.get("rev", 0)
                                    num_balance -= building_data.get("cost")
                                    sfx_place.play()
                                elif building_data.get("cost") >= num_balance:   
                                    sfx_error.play()
                            
            # If grid is right-clicked, sell building and remove any added counters (if applicable)                

            elif event.button == 3:
                grid_x, grid_y = x // GRID_SIZE, y // GRID_SIZE
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    if grid[grid_y][grid_x] is not None:
                        building_data = BUILDING_TYPES[grid[grid_y][grid_x]]
                        num_population -= building_data.get("pop", 0)
                        num_maintenance -= building_data.get("mai", 0)
                        num_revenue -= building_data.get("rev", 0)
                        num_balance += building_data.get("cost") * 0.75
                        grid[grid_y][grid_x] = None
                        sfx_remove.play()
      
        # If the mouse hovers over the UI buttons, hide the building preview

        if event.type == pygame.MOUSEMOTION:
            cursor_x, cursor_y = event.pos
            x, y = event.pos
            for button_rect, _ in button_rects:
                if button_rect.collidepoint(x, y):
                    show_selected_building = False
                    break
            else:
                show_selected_building = True

    # Snap cursor to the nearest grid slot with an offset to correct for image size

    cursor_x = (int(cursor_x / GRID_SIZE) + 0.5) * GRID_SIZE
    cursor_y = (int(cursor_y / GRID_SIZE) + 0.5) * GRID_SIZE

    # Render background tile

    for y in range(0, HEIGHT, background_image.get_height()):
        for x in range(0, WIDTH, background_image.get_width()):
            screen.blit(background_image, (x, y))

    # For every row, and every column, if the space isn't empty, render buildings

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell is not None:
                building_data = BUILDING_TYPES[cell]
                image = building_data["images"][direction_grid[y][x]]
                width, height = image.get_size()
                aspect_ratio = width / height

                # Scale the image to the grid cell, with correct the offset

                size_x = GRID_SIZE
                size_y = int(GRID_SIZE / aspect_ratio)
                offset_y = GRID_SIZE - size_y
                draw_x = x * GRID_SIZE 
                draw_y = y * GRID_SIZE + offset_y

                # Render the scaled image

                scaled_image = pygame.transform.scale(image, (size_x, size_y))
                screen.blit(scaled_image, (draw_x, draw_y))

    # If the grid's active, then draw the lines according to GRID_SIZE

    if show_grid:
        grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        grid_surface.set_alpha(50)

        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(grid_surface, GRID_COLOR, (x, 0), (x, HEIGHT), 2)
        for y in range(0, int(HEIGHT), GRID_SIZE):
            pygame.draw.line(grid_surface, GRID_COLOR, (0, y), (WIDTH, y), 2)

        # Render gridlines

        screen.blit(grid_surface, (0, 0))

    # Render the UI buttons

    for button_rect, building_type in button_rects:

        # Draw a rectangle using the UI Setup (189) and colour from the dict

        pygame.draw.rect(screen, BUILDING_TYPES[building_type]["color"], button_rect)

        # Scale the image on the left

        building_image = BUILDING_TYPES[building_type]["images"]["north"]
        image_height = button_rect.height * 1.1
        image_width = int(image_height * building_image.get_width() / building_image.get_height())
        scaled_image = pygame.transform.scale(building_image, (image_width, image_height))
        image_rect = scaled_image.get_rect(topleft=(button_rect.left + 5, button_rect.top - 9))

        # Scale text with correct type in the middle

        text = font.render(building_type, True, (255, 255, 255))
        text_rect = text.get_rect(center=(button_rect.center[0] - 5, button_rect.center[1]))

        # Scale and tint cost text (if applicable) on the right

        cost = BUILDING_TYPES[building_type]["cost"]
        if cost <= num_balance:
            cost_text = font.render(str(cost), True, (0, 255, 0))
        elif cost > num_balance:
            cost_text = font.render(str(cost), True, (255, 0, 0))
        cost_text_rect = cost_text.get_rect(midright=(button_rect.midright[0] - 5, button_rect.midright[1]))

        # Render button config

        screen.blit(scaled_image, image_rect)
        screen.blit(text, text_rect)
        screen.blit(cost_text, cost_text_rect)

    # Render counters

    population_text = font_counters.render(f"Population: {num_population}", True, (255, 255, 255))
    revenue_text = font_counters.render(f"Revenue: {num_revenue}", True, (255, 255, 255))
    maintenance_text = font_counters.render(f"Maintenance: {num_maintenance}", True, (255, 255, 255))
    money_text = font_counters.render(f"Balance: ${num_balance:.2f}", True, (20, 255, 20))

    screen.blit(revenue_text, (190, 40))
    screen.blit(maintenance_text, (190, 70))
    screen.blit(population_text, (190, 10))
    screen.blit(money_text, (190, 100))

    # Render the building preview

    if show_selected_building:
        building_data = BUILDING_TYPES[ACTIVE_BUILDING]
        image = building_data["images"][DIRECTIONS[direction_index]]
        width, height = image.get_size()
        aspect_ratio = width / height

        # Scale the image to the grid cell, with correct the offset

        size_x = GRID_SIZE
        size_y = int(GRID_SIZE / aspect_ratio)
        offset_y = GRID_SIZE - size_y
        draw_x = cursor_x - size_x // 2
        draw_y = cursor_y - offset_y

        # If there isn't a building in the place where the cursor is, then tint it green. Otherwise, it's taken, so tint it red

        if 0 <= int(cursor_y / GRID_SIZE) < GRID_HEIGHT and 0 <= int(cursor_x / GRID_SIZE) < GRID_WIDTH:
            y, x = int(cursor_y / GRID_SIZE), int(cursor_x / GRID_SIZE)
            if grid[y][x] is not None:
                image = tint_image_red(image)
            else:
                image = tint_image_green(image)

        # Render this tinted, scaled image onto the screen

        scaled_image = pygame.transform.scale(image, (size_x, size_y))
        scaled_image.set_alpha(100)
        draw_y = cursor_y - GRID_SIZE * 1.5
        screen.blit(scaled_image, (draw_x, draw_y))

    # Update screen    
    
    pygame.display.flip()    

pygame.quit()
sys.exit()
