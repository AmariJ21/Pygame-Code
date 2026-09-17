import pygame

pygame.init()

# Screen size
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Moving Square")
clock = pygame.time.Clock()

# Create the square
square = pygame.Rect(400, 300, 50, 50)

# Sideways speed of square
speed = 5

# Gravity: a small number we add to fall_speed every frame.
# The longer the square falls, the faster it goes!
gravity = 0.5
fall_speed = 0
jump_power = -12
standing_on_something = False

# A platform is just a rectangle the square can stand on.
ground = pygame.Rect(0, 550, 800, 50)
floating_platform = pygame.Rect(300, 400, 200, 20)
platforms = [ground, floating_platform]

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key press events
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

    # Clear the screen
    screen.fill((209, 0, 28))

    # Draw the platforms
    for platform in platforms:
        pygame.draw.rect(screen, (60, 180, 75), platform)

    # Draw the square
    pygame.draw.rect(screen, (46, 255, 227), square)

    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
