import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Map and Camera - Starter")
clock = pygame.time.Clock()

# --- The map ---
# Every character is one tile. Here's what each one means:
# 0 = empty air (nothing there)
# 1 = solid platform (you can stand on it)
# 2 = spike (touch it and you go back to the start!)
#
# This map is just flat ground with one platform to jump on.
# Try editing the rows below to make it your own:
#   - Change a 0 to a 1 somewhere in the air to add a new platform.
#   - Change a 1 in the bottom row to a 0 to open up a pit to jump over.
#   - Change a 0 to a 2 to add a spike (try putting one on the ground row!).
level_map = [
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000000000000000",
    "00000000111000000000",
    "00000000000000000000",
    "11111111111111111111",
]

# Turn the map's characters into real rectangles pygame can use
platforms = []
spikes = []

for row_index, row in enumerate(level_map):
    for col_index, tile in enumerate(row):
        x = col_index * TILE_SIZE
        y = row_index * TILE_SIZE
        if tile == "1":
            platforms.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
        elif tile == "2":
            spikes.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

world_width = TILE_SIZE * len(level_map[0])
world_height = TILE_SIZE * len(level_map)

# --- The player ---
start_position = (50, 300)
square = pygame.Rect(start_position[0], start_position[1], 50, 50)

speed = 5
gravity = 0.5
fall_speed = 0
jump_power = -12
standing_on_something = False

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        square.x -= speed
    if keys[pygame.K_RIGHT]:
        square.x += speed

    # Jumping only works while standing on something
    if keys[pygame.K_SPACE] and standing_on_something:
        fall_speed = jump_power

    # Step 1: remember where the bottom of the square was before it moves
    bottom_before = square.bottom

    # Step 2: gravity speeds up the fall, then we actually move the square
    fall_speed += gravity
    square.y += fall_speed
    standing_on_something = False

    # Step 3: did the square just land on top of a platform?
    for platform in platforms:
        square_was_above_platform = bottom_before <= platform.top
        square_touches_platform_now = square.colliderect(platform)
        if square_was_above_platform and square_touches_platform_now:
            square.bottom = platform.top
            fall_speed = 0
            standing_on_something = True

    # Step 4: touched a spike, or fell into a pit? Back to the start!
    touched_spike = False
    for spike in spikes:
        if square.colliderect(spike):
            touched_spike = True

    fell_off_the_map = square.top > world_height

    if touched_spike or fell_off_the_map:
        square.x, square.y = start_position
        fall_speed = 0

    # Step 5: move the camera so it follows the square
    # camera_x is how far the world has scrolled to the left
    camera_x = square.centerx - SCREEN_WIDTH // 2
    camera_x = max(0, min(camera_x, world_width - SCREEN_WIDTH))

    # Clear the screen
    screen.fill((115, 195, 255))

    # Draw the platforms, shifted by the camera so they scroll with the world
    for platform in platforms:
        draw_x = platform.x - camera_x
        pygame.draw.rect(screen, (60, 180, 75), (draw_x, platform.y, platform.width, platform.height))

    # Draw the spikes, shifted the same way
    for spike in spikes:
        draw_x = spike.x - camera_x
        pygame.draw.rect(screen, (200, 30, 30), (draw_x, spike.y, spike.width, spike.height))

    # Draw the square, shifted the same way
    square_draw_x = square.x - camera_x
    pygame.draw.rect(screen, (46, 255, 227), (square_draw_x, square.y, square.width, square.height))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
