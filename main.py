import pygame
import math


# ███████╗███████╗██╗     ██╗██╗  ██╗        ███████╗███████╗ ██████╗ 
# ██╔════╝██╔════╝██║     ██║╚██╗██╔╝        ██╔════╝██╔════╝██╔═████╗
# █████╗  █████╗  ██║     ██║ ╚███╔╝         ███████╗███████╗██║██╔██║
# ██╔══╝  ██╔══╝  ██║     ██║ ██╔██╗         ╚════██║╚════██║████╔╝██║
# ██║     ███████╗███████╗██║██╔╝ ██╗███████╗███████║███████║╚██████╔╝
# ╚═╝     ╚══════╝╚══════╝╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝ ╚═════╝ 
#Raycast Engine Python

# Initialize Pygame
pygame.init()

# Define the resolution of the game window
resolution = (480, 360)
Width, Height = resolution

# Create the game window
screen = pygame.display.set_mode(resolution)

# Set the player's initial position to the center of the screen
plr_x, plr_y = Width / 2, Height / 2
# Set the player's initial rotation to 0 degrees
plr_rot = 0
# Set the player's movement speed
speed = 2
FOV = 50  # Field of view of 50 degrees

# Raycast resolution: distance between rays
ray_resolution = 5

# 3D Rendering
WALL_HEIGHT = 50  # Constant wall height
PROJECTION_PLANE_WIDTH = Width
PROJECTION_PLANE_DISTANCE = (PROJECTION_PLANE_WIDTH / 2) / math.tan(math.radians(FOV / 2))

bar_size = 10

# Create a list of level objects including rectangles and circles
level_objects = [
    {"type": "rect", "rect": pygame.Rect(0, 0, Width, bar_size)},  # Top boundary
    {"type": "rect", "rect": pygame.Rect(0, Height - bar_size, Width, bar_size)},  # Bottom boundary
    {"type": "rect", "rect": pygame.Rect(0, 0, bar_size, Height)},  # Left boundary
    {"type": "rect", "rect": pygame.Rect(Width - bar_size, 0, bar_size, Height)},  # Right boundary
    {"type": "rect", "rect": pygame.Rect(100, 100, 50, 50)},  # A square in the level
    {"type": "rect", "rect": pygame.Rect(200, 200, 100, 30)},  # A rectangular object
    {"type": "rect", "rect": pygame.Rect(300, 270, 80, 80)},  # Another square in the level
    {"type": "circle", "center": (400, 150), "radius": 25}  # A circular object
]

# Load the player's image
imp = pygame.image.load("plr.png").convert_alpha()

def move():
    global plr_x, plr_y
    keys = pygame.key.get_pressed()
    move_vec = pygame.math.Vector2(0, 0)
    
    # Move the player forward
    if keys[pygame.K_UP]:
        move_vec += pygame.math.Vector2(math.cos(math.radians(plr_rot)), -math.sin(math.radians(plr_rot)))
    # Move the player backward
    if keys[pygame.K_DOWN]:
        move_vec -= pygame.math.Vector2(math.cos(math.radians(plr_rot)), -math.sin(math.radians(plr_rot)))
    
    # Normalize and apply speed to the movement vector
    if move_vec.length() > 0:
        move_vec = move_vec.normalize() * speed
    
    new_x, new_y = plr_x + move_vec.x, plr_y + move_vec.y
    player_rect = pygame.Rect(new_x - imp.get_width()/2, new_y - imp.get_height()/2, imp.get_width(), imp.get_height())
    
    can_move = True
    for obj in level_objects:
        # Check collision with rectangular objects
        if obj["type"] == "rect" and player_rect.colliderect(obj["rect"]):
            can_move = False
            break
        # Check collision with circular objects
        elif obj["type"] == "circle":
            circle_center = pygame.math.Vector2(obj["center"])  # Convert the tuple to a Vector2 object
            player_center = pygame.math.Vector2(player_rect.center)  # Convert the rectangle center to Vector2
            distance = player_center.distance_to(circle_center)  # This line will now work
            if distance < obj["radius"]:
                can_move = False
                break
    
    # Update the player's position if there are no collisions
    if can_move:
        plr_x, plr_y = new_x, new_y

def cast_ray(angle):
    ray_vec = pygame.math.Vector2(math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
    ray_point = pygame.math.Vector2(plr_x, plr_y)
    step = 1

    while True:
        ray_point += ray_vec * step
        
        for obj in level_objects:
            # Check collision with rectangular objects
            if obj["type"] == "rect" and obj["rect"].collidepoint(ray_point):
                return ray_point
            # Check collision with circular objects
            elif obj["type"] == "circle":
                circle_center = pygame.math.Vector2(obj["center"])
                if ray_point.distance_to(circle_center) <= obj["radius"]:
                    return ray_point

        # Break if the ray goes out of bounds
        if not (0 <= ray_point.x < Width and 0 <= ray_point.y < Height):
            return ray_point

def draw_3d_projection(ray_lengths):
    projection_surface = pygame.Surface((PROJECTION_PLANE_WIDTH, Height))
    projection_surface.fill((0, 0, 0))

    for x, ray_length in enumerate(ray_lengths):
         wall_height = (WALL_HEIGHT / ray_length) * PROJECTION_PLANE_DISTANCE  # Calculate wall height
         wall_top = (Height / 2) - (wall_height / 2)  # Calculate top position of the wall
         wall_bottom = (Height / 2) + (wall_height / 2)  # Calculate bottom position of the wall
         color_intensity = min(255, max(0, 255 - int(ray_length * 0.5)))  # Adjust wall color intensity based on distance
         wall_color = (color_intensity, color_intensity, color_intensity)

         # Draw the wall line
         pygame.draw.line(projection_surface, wall_color, (x, wall_top), (x, wall_bottom), 1)

    # Blit the projection surface onto the main screen
    screen.blit(projection_surface, (0, 0))

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill((0, 0, 0))  # Clear the screen

    move()  # Update player movement

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        plr_rot += 3  # Rotate player left
    if keys[pygame.K_RIGHT]:
        plr_rot -= 3  # Rotate player right

    half_fov = FOV // 2
    ray_lengths = []
    # Cast rays for 3D projection
    for i in range(0, PROJECTION_PLANE_WIDTH, int(ray_resolution)):
        ray_angle = plr_rot + half_fov - (i * FOV / PROJECTION_PLANE_WIDTH)
        ray_end = cast_ray(ray_angle)
        ray_length = math.sqrt((ray_end.x - plr_x)**2 + (ray_end.y - plr_y)**2)
        
        # Correct for fish-eye distortion
        corrected_ray_length = ray_length * math.cos(math.radians(plr_rot - ray_angle))
        
        ray_lengths.append(corrected_ray_length)

    interpolated_ray_lengths = []
    for i in range(PROJECTION_PLANE_WIDTH):
        idx = i // int(ray_resolution)
        interpolated_ray_lengths.append(ray_lengths[idx])

    draw_3d_projection(interpolated_ray_lengths)  # Draw the 3D projection

    # Minimap
    minimap_size = 100
    minimap_surface = pygame.Surface((minimap_size, minimap_size))
    minimap_surface.fill((0, 0, 0))
    for obj in level_objects:
        if obj["type"] == "rect":
            pygame.draw.rect(minimap_surface, (128, 128, 128), 
                             (obj["rect"].x * minimap_size / Width, obj["rect"].y * minimap_size / Height, 
                              obj["rect"].width * minimap_size / Width, obj["rect"].height * minimap_size / Height))
        elif obj["type"] == "circle":
            pygame.draw.circle(minimap_surface, (128, 128, 128), 
                               (int(obj["center"][0] * minimap_size / Width), int(obj["center"][1] * minimap_size / Height)), 
                               int(obj["radius"] * minimap_size / Width))
    pygame.draw.circle(minimap_surface, (255, 0, 0), 
                       (int(plr_x * minimap_size / Width), int(plr_y * minimap_size / Height)), 2)  # Draw the player on the minimap
    screen.blit(minimap_surface, (Width - minimap_size - 10, 10))  # Blit minimap onto the main screen

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
