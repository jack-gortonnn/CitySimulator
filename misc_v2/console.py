import pygame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
GRID_WIDTH, GRID_HEIGHT = 3000, 1600
TILE_WIDTH, TILE_HEIGHT = 40, 30
BACKGROUND_WIDTH, BACKGROUND_HEIGHT = 600, 400
CONSOLE_HEIGHT = 200
FPS_FONT_SIZE = 20
CONSOLE_FONT_SIZE = 20

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Variables
cameraX, cameraY, cameraTargetX, cameraTargetY = 0, 0, 0, 0
cameraSpeed, gridAlpha, fadeSpeed, fadeDirection = 0.1, 255, 10, 0
console_open = False
console_input = ""
command_history = []
keyPressed = False

# Pygame Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("City Simulator")
clock = pygame.time.Clock()

# Load assets
backgroundImage = pygame.image.load("assets/images/misc/background.png")
gridImage = pygame.image.load("assets/images/misc/grid_tiles.png").convert_alpha()
ui_image = pygame.image.load("assets/images/ui/ui_bg.png").convert_alpha()
ui_image = pygame.transform.scale(ui_image, (SCREEN_WIDTH, int(SCREEN_HEIGHT * 0.15)))
console_background_image = pygame.image.load("assets/images/ui/console.png").convert_alpha()
console_background_image = pygame.transform.scale(console_background_image, (707, 384))
building_image = pygame.image.load("assets/images/buildings/building1.png").convert_alpha()
building_width, building_height = building_image.get_size()

cheats_enabled = False
playermoney = 0

# Fonts
font = pygame.font.SysFont("Courier", FPS_FONT_SIZE)
console_font = pygame.font.SysFont("Courier", 14)

# Convert mouse coords to grid coords
def mouse_to_grid_coords(x, y): return (x + cameraX) // TILE_WIDTH, (y + cameraY) // TILE_HEIGHT
def grid_to_mouse_coords(x, y): return (x * TILE_WIDTH) - cameraX, (y * TILE_HEIGHT) - cameraY

# Command Handlers
def handle_sv_cheats(args):
    global cheats_enabled
    if len(args) == 1 and args[0] in {"0", "1"}:
        cheats_enabled = args[0] == "1"
    else:
        feedback = (f"sv_cheats {str(args[0])} is not a valid argument.")
        command_history.append((feedback, (208, 80, 80))) 

def handle_help(args):
    feedback = "Available commands:"
    command_history.append((feedback, LIGHT_GRAY))  # Add a header line

    # Add each command as its own line
    for command in command_registry.keys():
        command_history.append((f"- {command}", WHITE))  # Add each command with a bullet point
        
def handle_cl_balance(args):
    global playermoney

    # Check if cheats are enabled
    if not cheats_enabled:
        feedback = "Cheats are not enabled. Use 'sv_cheats 1' to enable cheats."
        command_history.append((feedback, (208, 80, 80)))  # Error message in red
        return

    # Check if arguments are provided
    if len(args) == 0:
        feedback = "Usage: cl_balance <amount>"
        command_history.append((feedback, (208, 80, 80)))  # Error message in red
        return

    # Validate input as a positive integer
    if args[0].isdigit():
        playermoney = int(args[0])  # Update balance
        feedback = f"Player balance updated to {playermoney}."
        command_history.append((feedback, WHITE))  # Success message in white
    else:
        feedback = f"cl_balance {args[0]} is not a valid argument."
        command_history.append((feedback, (208, 80, 80)))  # Error message in red


def handle_cl_showfps(args):
    global show_fps
    if len(args) == 1 and args[0] in {"0", "1"}:
        show_fps = args[0] == "1"
    else:
        feedback = (f"cl_showfps {str(args[0])} is not a valid argument.")
        command_history.append((feedback, (208, 80, 80)))  # Light gray for hints

def handle_unknown_command(command, args):
    feedback = f"Unknown command: {command}. Type 'help' for a list of commands."
    command_history.append((feedback, (208, 80, 80)))  # Red for errors

# Command Registry
command_registry = {
    "sv_cheats": handle_sv_cheats,
    "cl_showfps": handle_cl_showfps, 
    "cl_balance": handle_cl_balance,
    "help": handle_help
}

# Command Validation and Execution
def execute_command(command_input):
    parts = command_input.split()
    if not parts:
        return

    command = parts[0]
    args = parts[1:]

    handler = command_registry.get(command, handle_unknown_command)
    if handler == handle_unknown_command:
        handler(command, args)
    else:
        handler(args)

# Event Handling
def handle_events():
    global running, console_open, console_input, keyPressed, fadeDirection

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if console_open:
            handle_console_input(event)
        else:
            handle_game_input(event)

    keys = pygame.key.get_pressed()
    if not console_open and keys[pygame.K_g]:
        if not keyPressed:
            fadeDirection = 1 if gridAlpha == 0 else -1
            keyPressed = True
    elif not keys[pygame.K_g]:
        keyPressed = False

    return True

def handle_console_input(event):
    global console_open, console_input, command_history

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Define the close button area
        console_x = (SCREEN_WIDTH - console_background_image.get_width()) // 2
        console_y = ((SCREEN_HEIGHT - console_background_image.get_height()) // 2) - 50
        close_button_rect = pygame.Rect(
            console_x + console_background_image.get_width() - 30,  # Adjust for the button's position
            console_y + 10,  # Adjust for the button's Y position
            20, 20  # Width and height of the close button
        )

        if close_button_rect.collidepoint(mouse_x, mouse_y):
            console_open = False
            return

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:  # Enter key
            command_history.append((f"> {console_input}", WHITE))  # Command input in white
            execute_command(console_input)
            console_input = ""
        elif event.key == pygame.K_BACKSPACE:  # Backspace key
            console_input = console_input[:-1]
        elif event.key == pygame.K_BACKQUOTE:  # Toggle console
            console_open = False
        else:
            console_input += event.unicode

def handle_game_input(event):
    global console_open

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if SCREEN_HEIGHT - ui_image.get_height() <= mouse_y <= SCREEN_HEIGHT:
            print("Pressed UI")
        else:
            grid_x, grid_y = mouse_to_grid_coords(*pygame.mouse.get_pos())
            print(f"Clicked on tile at grid position: ({grid_x}, {grid_y})")

    if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKQUOTE:  # Toggle console
        console_open = True

def update_logic():
    global gridAlpha, fadeDirection, cameraX, cameraY, cameraTargetX, cameraTargetY

    if fadeDirection:
        gridAlpha = max(0, min(255, gridAlpha + fadeDirection * fadeSpeed))
        if gridAlpha in {0, 255}:
            fadeDirection = 0

    if not console_open:
        keys = pygame.key.get_pressed()
        cameraTargetX += (keys[pygame.K_d] - keys[pygame.K_a]) * 10
        cameraTargetY += (keys[pygame.K_s] - keys[pygame.K_w]) * 10
        cameraTargetX = max(0, min(GRID_WIDTH - SCREEN_WIDTH, cameraTargetX))
        cameraTargetY = max(0, min(GRID_HEIGHT - SCREEN_HEIGHT, cameraTargetY))

        cameraX += (cameraTargetX - cameraX) * cameraSpeed
        cameraY += (cameraTargetY - cameraY) * cameraSpeed

def draw():
    screen.fill(BLACK)
    draw_background()
    draw_grid()

    # Get mouse position and snap to the grid
    mouse_x, mouse_y = pygame.mouse.get_pos()
    grid_x, grid_y = mouse_to_grid_coords(mouse_x, mouse_y)
    
    # Draw building at the snapped grid position
    building_pos_x = grid_x * TILE_WIDTH - cameraX
    building_pos_y = grid_y * TILE_HEIGHT - cameraY
    screen.blit(building_image, (building_pos_x, building_pos_y))

    screen.blit(ui_image, (0, SCREEN_HEIGHT - ui_image.get_height()))
    if console_open:
        draw_console()
    if show_fps:
        draw_fps()

    clock.tick()
    pygame.display.flip()

def draw_background():
    for x in range(-1, (SCREEN_WIDTH // BACKGROUND_WIDTH) + 2):
        for y in range(-1, (SCREEN_HEIGHT // BACKGROUND_HEIGHT) + 2):
            screen.blit(
                backgroundImage,
                (x * BACKGROUND_WIDTH - cameraX % BACKGROUND_WIDTH, y * BACKGROUND_HEIGHT - cameraY % BACKGROUND_HEIGHT)
            )

def draw_grid():
    grid_tile = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
    grid_tile.blit(gridImage, (0, 0))
    grid_tile.set_alpha(gridAlpha)

    for x in range(-1, (SCREEN_WIDTH // TILE_WIDTH) + 2):
        for y in range(-1, (SCREEN_HEIGHT // TILE_HEIGHT) + 2):
            screen.blit(
                grid_tile,
                (x * TILE_WIDTH - cameraX % TILE_WIDTH, y * TILE_HEIGHT - cameraY % TILE_HEIGHT)
            )

def draw_console():
    # Calculate the position to center the console background
    console_x = (SCREEN_WIDTH - console_background_image.get_width()) // 2
    console_y = ((SCREEN_HEIGHT - console_background_image.get_height()) // 2) - 50

    # Draw the console background image
    screen.blit(console_background_image, (console_x, console_y))

    # Draw the command input text
    input_text = console_font.render(f"{console_input}", True, WHITE)
    screen.blit(input_text, (console_x + 20, console_y + 351))

    # Draw the command history
    y_offset = 315
    for command, color in reversed(command_history[-15:]):  # Now each command has a color
        history_text = console_font.render(command, True, color)
        screen.blit(history_text, (console_x + 20, console_y + y_offset))
        y_offset -= 19


def draw_fps():
    fps_text = font.render(f"{int(clock.get_fps())} fps on maps/de_dust2.vmf", True, GREEN)
    screen.blit(fps_text, (10, 30))

command_history.append(("Loaded assets/images/misc/background.png", (LIGHT_GRAY)))
command_history.append(("Loaded assets/images/misc/grid_tiles.png", (LIGHT_GRAY)))


show_fps = 0

# Main Game Loop
running = True
while running:
    running = handle_events()
    update_logic()
    draw()
    clock.tick()

pygame.quit()