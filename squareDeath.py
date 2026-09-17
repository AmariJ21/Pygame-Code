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

# --- Gravity setup ---
# Gravity is just a number we add to the square's vertical speed
# every frame, so it speeds up the longer it falls (acceleration!).
gravity = 0.5
velocity_y = 0
jump_strength = -12
on_ground = False

# --- Platforms the square can land on ---
# A platform is just a rectangle, same as the square.
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
    if keys[pygame.K_SPACE] and on_ground:
        velocity_y = jump_strength

    # Gravity pulls the square down a little more each frame
    velocity_y += gravity
    square.y += velocity_y
    on_ground = False

    # Check if the square has landed on top of any platform
    for platform in platforms:
        if square.colliderect(platform):
            falling = velocity_y > 0
            was_above = (square.bottom - velocity_y) <= platform.top
            if falling and was_above:
                square.bottom = platform.top
                velocity_y = 0
                on_ground = True

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
