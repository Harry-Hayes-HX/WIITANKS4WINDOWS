import pygame
import math

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)

# Create the screen and set the title
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tanks Game')

# Player tank properties
player_pos = [350, 250]  # Starting position (x, y)
player_size = 40  # Width and height of the square tank
player_speed = 0.1  # Movement speed
player_angle = 0  # Initial direction (angle in degrees)
rotation_speed = 0.1  # Rotation speed in degrees

#obstacles
obstacles = [
     # Border obstacles
    pygame.draw.rect(screen, BROWN, (50, 50, 700, 20)),  # Top border
    pygame.draw.rect(screen, BROWN, (50, 50, 20, 500)), # Left border
    pygame.draw.rect(screen, BROWN, (730, 50, 20, 500)), # Right border
    pygame.draw.rect(screen, BROWN, (50, 530, 700, 20)), # Bottom border

    # Inner obstacles
    pygame.draw.rect(screen, BROWN, (200, 150, 50, 100)),  # Top rectangle
    pygame.draw.rect(screen, BROWN, (200, 350, 50, 100)),  # Bottom rectangle

    # Long rectangle at the bottom
    pygame.draw.rect(screen, BROWN, (400, 150, 50, 300))
]

def draw_environment():
    # Background
    screen.fill(WHITE)

    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, BROWN, obstacle)

   
     # Draw rotated player tank
    player_image = pygame.Surface((player_size, player_size), pygame.SRCALPHA)  # Added pygame.SRCALPHA for transparency
    player_image.fill((0, 0, 0, 0))  # Fill with transparent color
    pygame.draw.rect(player_image, BLUE, (0, 0, player_size, player_size))
    pygame.draw.circle(player_image, WHITE, (player_size // 2, 0), 5)
    rotated_image = pygame.transform.rotate(player_image, player_angle)
    screen.blit(rotated_image, (player_pos[0] - rotated_image.get_width() // 2, player_pos[1] - rotated_image.get_height() // 2))


def check_collision(new_x, new_y, angle):
    player_image = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
    player_image.fill((0, 0, 0, 0))
    pygame.draw.rect(player_image, BLUE, (0, 0, player_size, player_size))
    rotated_image = pygame.transform.rotate(player_image, angle)
    player_rect = rotated_image.get_rect(center=(new_x, new_y))
    
    for obstacle in obstacles:
        if player_rect.colliderect(obstacle):
            return True
    return False

def main():
    global player_pos, player_angle
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        new_angle = player_angle  # Copy current angle for prediction

        if keys[pygame.K_w]:
            dx = -player_speed * math.sin(math.radians(player_angle))
            dy = -player_speed * math.cos(math.radians(player_angle))
        if keys[pygame.K_s]:
            dx = player_speed * math.sin(math.radians(player_angle))
            dy = player_speed * math.cos(math.radians(player_angle))
        if keys[pygame.K_a]:
            new_angle += rotation_speed
        if keys[pygame.K_d]:
            new_angle -= rotation_speed

        # Predict next position
        new_x = player_pos[0] + dx
        new_y = player_pos[1] + dy

        # Check for collisions at predicted position
        if not check_collision(new_x, new_y, new_angle):
            player_pos[0] = new_x
            player_pos[1] = new_y
            player_angle = new_angle
        else:
            # If collision occurs, check movement without rotation
            if not check_collision(new_x, new_y, player_angle):
                player_pos[0] = new_x
                player_pos[1] = new_y

        # Keep angle within 0-360 range
        player_angle %= 360

        draw_environment()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()