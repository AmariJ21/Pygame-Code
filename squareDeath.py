import pygame

pygame.init()

# Screen size
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Moving Square")

# Create the square
square = pygame.Rect(400, 300, 50, 50)

# Speed of square
speed = 1

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
    if keys[pygame.K_UP]:
        square.y -= speed
    if keys[pygame.K_DOWN]:
        square.y += speed

    # Clear the screen
    screen.fill((209, 0, 28))

    # Draw the square
    pygame.draw.rect(screen, (46, 255, 227), square)

    # Update the display
    pygame.display.flip()

pygame.quit()
