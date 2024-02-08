import pygame
import math
import time

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
RED = (100, 0, 0)


# Create the screen and set the title
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tanks Game')


# Player tank properties
player_pos = [350, 250]  # Starting position (x, y)
player_size = 40  # Width and height of the square tank
player_speed = 0.1  # Movement speed
player_angle = 0  # Initial direction (angle in degrees)
rotation_speed = 0.1  # Rotation speed in degrees


# Settings button and bounding box visibility flag
settings_button = pygame.Rect(SCREEN_WIDTH - 110, 10, 100, 50)  # Position it in the top-right corner
show_bounding_box = True  # Control the visibility of the bounding box

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

# At the top with other initializations
bullet_speed = 0.4
bullets = []  # Each bullet will be a dictionary with keys for position, direction, and bounce count
last_fire_time = 0  # Track the last time a bullet was fired



def draw_tank_and_barrel():
    # Tank body and barrel combined surface size, adjusted for the doubled barrel length
    combined_length = player_size * 2  # Adjusted to accommodate the longer barrel
    tank_and_barrel_surface = pygame.Surface((combined_length, combined_length), pygame.SRCALPHA)
    tank_and_barrel_surface.fill((0, 0, 0, 0))  # Transparent background
    
    # Draw the tank body on this surface
    tank_body_rect = pygame.Rect((combined_length - player_size) / 2, 
                                 (combined_length - player_size) / 2, 
                                 player_size, player_size)
    pygame.draw.rect(tank_and_barrel_surface, BLUE, tank_body_rect)
    
    # Calculate the barrel's position and draw it with doubled length
    barrel_length = player_size  # The barrel length is now equal to the tank's width
    barrel_width = player_size / 3  # Keeping the barrel width as before
    # The barrel starts at the front center of the tank body
    barrel_start_x = (combined_length - player_size) / 2 + player_size
    barrel_start_y = (combined_length - barrel_width) / 2
    barrel_rect = pygame.Rect(barrel_start_x, barrel_start_y, barrel_length, barrel_width)
    pygame.draw.rect(tank_and_barrel_surface, BLUE, barrel_rect)
    
    # Rotate the surface based on the tank's orientation
    rotated_surface = pygame.transform.rotate(tank_and_barrel_surface, -player_angle)
    
    # Blit the rotated surface to the screen, centered on the tank's position
    screen.blit(rotated_surface, (player_pos[0] - rotated_surface.get_width() / 2, 
                                  player_pos[1] - rotated_surface.get_height() / 2))




def draw_environment():
    screen.fill(WHITE)
    
    # Draw obstacles and their bounding boxes for debugging
    for obstacle in obstacles:
        pygame.draw.rect(screen, BROWN, obstacle)  # Original obstacle drawing
        pygame.draw.rect(screen, (255, 0, 0), obstacle, 2)  # Debug: draw bounding box in red

    # Draw the tank and barrel
    draw_tank_and_barrel()


    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, RED, (int(bullet['x']), int(bullet['y'])), 5)

    # Draw the settings button
    pygame.draw.rect(screen, (0, 0, 0), settings_button)  # Draw the button as a black rectangle
    font = pygame.font.Font(None, 24)  # Adjust font size as needed
    text = font.render('Settings', True, (255, 255, 255))
    text_rect = text.get_rect(center=settings_button.center)
    screen.blit(text, text_rect)
    
    # Draw the bounding box if toggled on
    if show_bounding_box:
        tank_rect = calculate_rotated_bounding_box(player_pos[0], player_pos[1], player_size, player_size, player_angle)
        pygame.draw.rect(screen, (255, 0, 0), tank_rect, 2)  # Draw the tank's bounding box in red

    


def calculate_rotated_bounding_box(x, y, width, height, angle):
    # Convert angle to radians
    angle_rad = math.radians(angle)
    
    # Define the center of the tank for rotation
    center_x, center_y = x + width / 24, y + height / 24
    
    # Define the corners relative to the center
    corners = [(-width / 2, -height / 2), (width / 2, -height / 2),
               (width / 2, height / 2), (-width / 2, height / 2)]
    
    # Rotate corners
    rotated_corners = [(center_x + cos * math.cos(angle_rad) - sin * math.sin(angle_rad),
                        center_y + cos * math.sin(angle_rad) + sin * math.cos(angle_rad))
                       for cos, sin in corners]
    
    # Find min and max x, y to form the bounding box
    min_x = min(corner[0] for corner in rotated_corners)
    max_x = max(corner[0] for corner in rotated_corners)
    min_y = min(corner[1] for corner in rotated_corners)
    max_y = max(corner[1] for corner in rotated_corners)
    
    # Return as pygame.Rect
    return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)


def calculate_adjusted_bounding_box(x, y, width, height, angle):
    """
    Adjust the dimensions slightly to calculate a "tighter" bounding box.
    """
    adjustment_factor = 0.9  # Adjust by 10% smaller to tighten the bounding box
    adjusted_width = width * adjustment_factor
    adjusted_height = height * adjustment_factor

    return calculate_rotated_bounding_box(x + (width - adjusted_width) / 2, 
                                          y + (height - adjusted_height) / 2, 
                                          adjusted_width, 
                                          adjusted_height, 
                                          angle)


def check_tank_collision(new_x, new_y, angle):
    tank_rect = calculate_rotated_bounding_box(new_x, new_y, player_size, player_size, angle)
    for obstacle in obstacles:
        if tank_rect.colliderect(obstacle):
            return True  # Collision detected
    return False


def fire_bullet():
    global bullets, last_fire_time
    current_time = time.time()
    if current_time - last_fire_time > 1.5:  # Ensure a bullet can only be fired every 1.5 seconds
        direction_radians = math.radians(player_angle)
        
        # Given the updated barrel length
        barrel_length = player_size / 2  # As provided
        
        # Calculate the bullet's starting position at the barrel's tip
        # Adjusting for the updated barrel length which extends from the tank's front center
        bullet_start_x = player_pos[0] + math.cos(direction_radians) * (player_size / 2 + barrel_length)
        bullet_start_y = player_pos[1] + math.sin(direction_radians) * (player_size / 2 + barrel_length)

        # Append the new bullet to the bullets list with its direction and speed
        bullets.append({
            'x': bullet_start_x,
            'y': bullet_start_y,
            'dx': math.cos(direction_radians) * bullet_speed,
            'dy': math.sin(direction_radians) * bullet_speed,
            'bounced': False  # Initially, the bullet has not bounced
        })
        last_fire_time = current_time  # Update the last fire time to the current time




def update_bullets():
    global bullets
    bullets_to_keep = []  # A new list to keep bullets that shouldn't be removed
    for bullet in bullets:
        # Assume the bullet will move this frame
        will_move = True

        # Move bullet
        next_x = bullet['x'] + bullet['dx']
        next_y = bullet['y'] + bullet['dy']
        bullet_rect = pygame.Rect(next_x - 2, next_y - 2, 4, 4)  # Bullet's next position

        for obstacle in obstacles:
            if obstacle.colliderect(bullet_rect):
                if not bullet['bounced']:
                    # If the bullet hasn't bounced yet, calculate the bounce
                    # Determine if it's a horizontal or vertical collision
                    # (This simplistic approach might need refinement for accuracy)
                    if bullet['x'] < obstacle.left or bullet['x'] > obstacle.right:
                        bullet['dx'] = -bullet['dx']  # Reverse horizontal direction
                    if bullet['y'] < obstacle.top or bullet['y'] > obstacle.bottom:
                        bullet['dy'] = -bullet['dy']  # Reverse vertical direction
                    
                    bullet['bounced'] = True  # Mark the bullet as having bounced
                    will_move = True  # Allow the bullet to move after bouncing
                else:
                    # If the bullet has already bounced, it will be removed
                    will_move = False  # Prevent further movement; the bullet will be removed
                break  # Stop checking other obstacles since we've processed this bullet

        if will_move:
            # If the bullet is allowed to move (hasn't hit a second obstacle),
            # update its position and keep it in the list
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            bullets_to_keep.append(bullet)
        # Otherwise, the bullet is not added back, effectively removing it

    bullets = bullets_to_keep  # Update the bullets list with the remaining bullets






def main():
    global player_pos, player_angle, bullets, last_fire_time, show_bounding_box  
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the click is within the bounds of the settings button
                if settings_button.collidepoint(event.pos):
                    show_bounding_box = not show_bounding_box  # Toggle the flag

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        proposed_angle = player_angle

        # Handle rotation
        if keys[pygame.K_a]:
            proposed_angle -= rotation_speed
        if keys[pygame.K_d]:
            proposed_angle += rotation_speed

        # Calculate proposed movement based on current input and orientation
        if keys[pygame.K_w]:
            dx += player_speed * math.cos(math.radians(proposed_angle))
            dy += player_speed * math.sin(math.radians(proposed_angle))
        if keys[pygame.K_s]:
            dx -= player_speed * math.cos(math.radians(proposed_angle))
            dy -= player_speed * math.sin(math.radians(proposed_angle))

        # Calculate the new position based on proposed movement
        new_x = player_pos[0] + dx
        new_y = player_pos[1] + dy

        # Use the updated collision check with the proposed new position and angle
        if not check_tank_collision(new_x, new_y, proposed_angle):
            # No collision detected; update position and angle
            player_pos[0] = new_x
            player_pos[1] = new_y
            player_angle = proposed_angle
        # Else, the movement is blocked by an obstacle, so don't update position or angle

        # Fire bullets and update their positions
        if keys[pygame.K_SPACE] and time.time() - last_fire_time > 1.5:
            fire_bullet()
            last_fire_time = time.time()

        # In your game loop, after handling movements and before drawing
        print(f"Tank Position: {player_pos}, Size: {player_size}, Angle: {player_angle}")
        for obstacle in obstacles:
            print(f"Obstacle: {obstacle}")


        update_bullets()
        draw_environment()  # Make sure this draws the tank and handles rotation correctly

        pygame.display.flip()

    pygame.quit()

# Ensure the rest of your necessary functions (draw_environment, fire_bullet, update_bullets, etc.) are defined here

if __name__ == "__main__":
    main()
