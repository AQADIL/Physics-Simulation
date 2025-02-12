import pygame
import random
import math
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ақәділ братанның ойындары")

# Load DVD images
DVD_IMAGES = []
try:
    for file in ["DVD-red.png", "DVD-yellow.png", "DVD-blue.png", "DVD-green.png"]:
        img = pygame.image.load(file)
        DVD_IMAGES.append(pygame.transform.scale(img, (250, 150)))
except Exception as e:
    print(f"Error loading DVD images: {e}")
    exit()

menu_music = pygame.mixer.Sound("menu.wav")
is_menu_music_playing = False

# Physics constants
GRAVITY = 0.8
AIR_RESISTANCE = 0.99
ENERGY_LOSS = 0.7
FRICTION = 0.92
ELASTICITY = 0.85
MAX_SPEED = 20
LAUNCH_POWER = 0.15  # For Box Breaker game

# Game States
MENU = 0
FALLING_SHAPES = 1
BOX_BREAKER = 2
BOUNCING_DVD = 3
current_game = MENU

# Colors
COLORS = [
    (255, 50, 50),  # Red
    (50, 255, 50),  # Green
    (50, 50, 255),  # Blue
    (255, 255, 50),  # Yellow
    (255, 50, 255),  # Magenta
    (50, 255, 255),  # Cyan
    (180, 50, 180),  # Purple
    (50, 180, 180)  # Teal
]

# Fonts
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 32)

CORRECT_PIN = "1234"
def draw_pin_prompt():
    screen.fill((30, 30, 50))
    prompt_text = font.render("Enter PIN:", True, (255, 255, 255))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.flip()

def get_pin_input():
    pin = ""
    draw_pin_prompt()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return pin
                elif event.key == pygame.K_BACKSPACE:
                    pin = pin[:-1]
                else:
                    if event.unicode.isdigit() and len(pin) < 4:
                        pin += event.unicode
                # Redraw the PIN prompt with the current PIN input
                screen.fill((30, 30, 50))
                prompt_text = font.render("Enter PIN:", True, (255, 255, 255))
                screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 50))
                pin_text = font.render("*" * len(pin), True, (255, 255, 255))
                screen.blit(pin_text, (WIDTH // 2 - pin_text.get_width() // 2, HEIGHT // 2))
                pygame.display.flip()

def verify_pin():
    pin = get_pin_input()
    if pin == CORRECT_PIN:
        return True
    else:
        return False

def main():
    if not verify_pin():
        print("Incorrect PIN. Exiting game.")
        pygame.quit()


main()


class PhysicsEntity:
    def __init__(self, x, y, size, color, shape, health=100):
        # Initialize entity properties
        self.x = x  # X position
        self.y = y  # Y position
        self.size = size
        self.color = color
        self.shape = shape  # circle, square, triangle
        self.vx = 0.0  # Velocity in the X
        self.vy = 0.0  # Velocity in the Y
        self.on_ground = False  # Whether the entity is on the ground
        self.rotation = 0  # Rotation angle
        self.rotation_speed = random.uniform(-2, 2)  # Speed of rotation
        self.mass = size ** 2  # Mass of the entity (based on size)
        self.health = health  # Health of the entity

    def apply_physics(self):
        # Apply gravity and air resistance
        self.vy += GRAVITY  # Add gravity to vertical velocity
        self.vy = min(self.vy, MAX_SPEED)  # Limit vertical speed
        self.vx *= AIR_RESISTANCE  # Apply air resistance to horizontal velocity
        self.vy *= AIR_RESISTANCE  # Apply air resistance to vertical velocity
        self.x += self.vx  # Update X position
        self.y += self.vy  # Update Y position
        self.rotation += self.rotation_speed  # Update rotation
        self.vx = max(min(self.vx, MAX_SPEED), -MAX_SPEED)  # Limit horizontal speed
        self.vy = max(min(self.vy, MAX_SPEED), -MAX_SPEED)  # Limit vertical speed

    def check_boundaries(self):
        # Check for collisions with screen boundaries
        next_x = self.x + self.vx  # Calculate next X position
        next_y = self.y + self.vy  # Calculate next Y position

        # Left and right wall collisions
        if next_x < self.size:
            self.x = self.size
            self.vx *= -ELASTICITY  # Reverse X velocity with elasticity
        elif next_x > WIDTH - self.size:
            self.x = WIDTH - self.size  # Prevent entity from going off the right side
            self.vx *= -ELASTICITY  # Reverse X velocity with elasticity

        # Top and bottom wall collisions
        if next_y < self.size:
            self.y = self.size  # Prevent entity from going off the top
            self.vy *= -ELASTICITY  # Reverse Y velocity with elasticity
        elif next_y > HEIGHT - self.size:
            self.y = HEIGHT - self.size  # Prevent entity from going off the bottom
            self.vy *= -ELASTICITY * 0.5  # Reverse Y velocity with reduced elasticity
            self.vx *= FRICTION  # Apply friction to X velocity
            self.on_ground = True  # Mark entity as on the ground
        else:
            self.on_ground = False  # Mark entity as not on the ground

    def draw(self):
        # Draw the entity based on its shape
        if self.shape == "circle":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        elif self.shape == "square":
            rect = pygame.Rect(self.x - self.size, self.y - self.size,
                               self.size * 2, self.size * 2)
            pygame.draw.rect(screen, self.color, rect)
        elif self.shape == "triangle":
            points = [
                (self.x, self.y - self.size),
                (self.x - self.size, self.y + self.size),
                (self.x + self.size, self.y + self.size)
            ]
            pygame.draw.polygon(screen, self.color, points)


class Projectile(PhysicsEntity):                     #снаряд
    def __init__(self, x, y, size, color, target_x, target_y):
        # Initialize projectile with target position
        super().__init__(x, y, size, color, "circle")
        dx = target_x - x  # Calculate X distance to target
        dy = target_y - y  # Calculate Y distance to target
        distance = math.hypot(dx, dy)  # Calculate total distance to target
        self.vx = dx * LAUNCH_POWER  # Set X velocity based on launch power
        self.vy = dy * LAUNCH_POWER  # Set Y velocity based on launch power


class Box(PhysicsEntity):
    def __init__(self, x, y, size):
        # Initialize box with default properties
        super().__init__(x, y, size, (200, 150, 100), "square", health=50)



class GameManager:
    def __init__(self):
        # Initialize game state variables
        self.entities = []
        self.projectiles = []
        self.boxes = []
        self.collisions_enabled = True
        self.spawn_timer = 0  # Timer for spawning new entities
        self.paused = False  # Pause state of the game
        self.ground_level = HEIGHT - 50
        self.dragging = False
        self.drag_start = (0, 0)
        self.score = 0  # Player's score
        self.shots = 0  # Number of shots taken (Box Breaker)
        self.round = 1  # Current round
        self.time_left = 21  # Timer for the game (20 seconds)
        self.game_over = False  # Flag to check if the game is over
        self.victory = False  # Flag to check if the player has won

        # DVD Game specific variables
        self.dvd_x = WIDTH // 2
        self.dvd_y = HEIGHT // 2
        self.dvd_speed_x = 3
        self.dvd_speed_y = 3
        self.current_dvd_image = 0
        self.total_hits = 0  # Total hits (bounces) of the DVD logo
        self.credits_sequence = False
        self.credits_alpha = 0  # Transparency level for the credits
        self.credits_text = [  # Text to display during the credits
            "Author: Sagacious Akadil",
            "Physics Simulator developed in 2 weeks",
            "Hope you enjoyed the game!",
            "Thanks for playing !!!"
        ]

        # Slider for DVD speed control
        self.slider_x = 50  # X position of the slider
        self.slider_y = HEIGHT - 50  # Y position of the slider
        self.slider_width = 200  # Width of the slider
        self.slider_height = 20  # Height of the slider
        self.slider_handle_x = self.slider_x  # X position of the slider handle
        self.slider_handle_width = 10  # Width of the slider handle
        self.slider_dragging = False  # Flag to check if the slider is being dragged

        # Initialize the game level (Box Breaker mode)
        self.create_level()

    def create_level(self):
        """Create the initial level layout for Box Breaker mode."""
        self.boxes.clear()
        for i in range(5):
            for j in range(3):
                box = Box(700 + i * 60, HEIGHT - 200 - j * 60, 25)
                self.boxes.append(box)

    def reset_game(self):
        """Reset the game state when starting a new game."""
        self.game_over = False
        self.victory = False
        self.score = 0
        self.shots = 0
        self.time_left = 30
        self.create_level()

    def handle_collisions(self):
        """Handle collisions between all objects in the game."""
        all_objects = self.entities + self.projectiles + self.boxes
        for i in range(len(all_objects)):
            for j in range(i + 1, len(all_objects)):
                self.check_collision(all_objects[i], all_objects[j])

    def check_collision(self, obj1, obj2):
        """Check and resolve collisions between two objects."""
        dx = obj2.x - obj1.x
        dy = obj2.y - obj1.y
        distance = math.hypot(dx, dy)
        min_dist = obj1.size + obj2.size

        if distance < min_dist:
            # Handle projectile-box collisions
            if isinstance(obj1, Projectile) and isinstance(obj2, Box):
                obj2.health -= 20
                if obj2.health <= 0:
                    self.boxes.remove(obj2)
                    self.score += 10
                if obj1 in self.projectiles:
                    self.projectiles.remove(obj1)

            if isinstance(obj2, Projectile) and isinstance(obj1, Box):
                obj1.health -= 20
                if obj1.health <= 0:
                    self.boxes.remove(obj1)
                    self.score += 10
                if obj2 in self.projectiles:
                    self.projectiles.remove(obj2)

            # Resolve overlap between objects
            angle = math.atan2(dy, dx)
            overlap = 0.5 * (min_dist - distance)

            obj1.x -= overlap * math.cos(angle)
            obj1.y -= overlap * math.sin(angle)
            obj2.x += overlap * math.cos(angle)
            obj2.y += overlap * math.sin(angle)

            # Calculate new velocities after collision
            tangent = math.atan2(dy, dx)
            normal = tangent + math.pi / 2

            v1 = math.hypot(obj1.vx, obj1.vy)
            v2 = math.hypot(obj2.vx, obj2.vy)
            dir1 = math.atan2(obj1.vy, obj1.vx)
            dir2 = math.atan2(obj2.vy, obj2.vx)

            new_v1 = v2 * ELASTICITY
            new_v2 = v1 * ELASTICITY

            obj1.vx = math.cos(dir2) * new_v1
            obj1.vy = math.sin(dir2) * new_v1
            obj2.vx = math.cos(dir1) * new_v2
            obj2.vy = math.sin(dir1) * new_v2

    def update_entities(self, current_game):
        """Update all entities in the game based on the current game mode."""
        if self.paused or self.game_over:
            return

        # Spawn new entities in Falling Shapes mode
        self.spawn_timer += 1
        if current_game == FALLING_SHAPES and self.spawn_timer > 45:
            self.spawn_random_entity()
            self.spawn_timer = 0

        # Apply physics to all entities
        for entity in self.entities:
            entity.apply_physics()
            entity.check_boundaries()

        for obj in self.entities + self.projectiles + self.boxes:
            obj.apply_physics()
            obj.check_boundaries()

        self.handle_collisions()
        # Remove projectiles that are out of bounds
        self.projectiles = [p for p in self.projectiles if 0 < p.x < WIDTH and 0 < p.y < HEIGHT]

        # Check for victory condition in Box Breaker mode
        if current_game == BOX_BREAKER and not self.boxes:
            self.victory = True
            self.game_over = True
            self.time_left = 0

        # Update the game timer
        if self.time_left > 0:
            self.time_left -= 1 / 60  # Decrease timer every second
        else:
            if not self.victory:  # If time runs out and victory is not achieved
                self.game_over = True

    def spawn_random_entity(self):
        """Spawn a random entity in Falling Shapes mode."""
        shapes = ["circle", "square", "triangle"]
        new_entity = PhysicsEntity(
            x=random.randint(50, WIDTH - 50),
            y=-50,
            size=random.randint(15, 35),
            color=random.choice(COLORS),
            shape=random.choice(shapes)
        )
        new_entity.vx = random.uniform(-3, 3)
        self.entities.append(new_entity)

    def start_drag(self, pos):
        """Start dragging (aiming) in Box Breaker mode."""
        if current_game == BOX_BREAKER:
            self.dragging = True
            self.drag_start = pos

    def end_drag(self, pos):
        """End dragging and launch a projectile in Box Breaker mode."""
        if current_game == BOX_BREAKER and self.dragging:
            self.dragging = False
            projectile = Projectile(100, HEIGHT - 100, 15, (255, 0, 0), *pos)
            self.projectiles.append(projectile)
            self.shots += 1  # Increment the shot counter

    def draw_aim(self):
        """Draw the aiming line in Box Breaker mode."""
        if self.dragging:
            pygame.draw.line(screen, (255, 255, 255), (100, HEIGHT - 100),
                             pygame.mouse.get_pos(), 2)
            pygame.draw.circle(screen, (255, 0, 0), (100, HEIGHT - 100), 20)

    def update_dvd(self):
        """Update the position and state of the DVD logo."""
        self.dvd_x += self.dvd_speed_x
        self.dvd_y += self.dvd_speed_y

        # Check for wall collisions and increment hit counter
        if self.dvd_x <= 0 or self.dvd_x + 250 >= WIDTH or self.dvd_y <= 0 or self.dvd_y + 150 >= HEIGHT:
            self.total_hits += 1

        # Bounce off walls
        if self.dvd_x <= 0 or self.dvd_x + 250 >= WIDTH:
            self.dvd_speed_x *= -1
            self.current_dvd_image = (self.current_dvd_image + 1) % len(DVD_IMAGES)

        if self.dvd_y <= 0 or self.dvd_y + 150 >= HEIGHT:
            self.dvd_speed_y *= -1
            self.current_dvd_image = (self.current_dvd_image + 1) % len(DVD_IMAGES)

        # Trigger credits sequence after 30 hits
        if self.total_hits >= 30:
            self.credits_sequence = True

    def draw_dvd(self):
        """Draw the DVD logo on the screen."""
        screen.blit(DVD_IMAGES[self.current_dvd_image], (self.dvd_x, self.dvd_y))

    def draw_counters(self):
        """Draw the hit counter on the screen."""
        total_hits_text = small_font.render(f"Total Hits: {self.total_hits}", True, (255, 255, 255))
        screen.blit(total_hits_text, (10, 10))

    def draw_credits(self):
        """Draw the credits sequence on the screen."""
        if self.credits_sequence:
            if self.credits_alpha < 255:
                self.credits_alpha += 2  # Gradually increase transparency

            # Draw a semi-transparent black overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.credits_alpha // 2))
            screen.blit(overlay, (0, 0))

            # Draw each line of the credits text
            for i, line in enumerate(self.credits_text):
                text = font.render(line, True, (255, 255, 255))
                text.set_alpha(self.credits_alpha)
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
                screen.blit(text, text_rect)

    def draw_slider(self):
        """Draw the speed control slider for the DVD game."""
        pygame.draw.rect(screen, (200, 200, 200), (self.slider_x, self.slider_y, self.slider_width, self.slider_height))
        pygame.draw.rect(screen, (100, 100, 100), (self.slider_handle_x, self.slider_y, self.slider_handle_width, self.slider_height))

    def update_slider(self, mouse_pos):
        """Update the slider position and adjust DVD speed accordingly."""
        if self.slider_dragging:
            self.slider_handle_x = max(self.slider_x, min(mouse_pos[0], self.slider_x + self.slider_width - self.slider_handle_width))
            # Adjust DVD speed based on slider position
            speed_ratio = (self.slider_handle_x - self.slider_x) / (self.slider_width - self.slider_handle_width)
            self.dvd_speed_x = 3 + speed_ratio * 7  # Speed ranges from 3 to 10
            self.dvd_speed_y = 3 + speed_ratio * 7

    def init_dvd(self):
        """Initialize the DVD game state."""
        self.dvd_x = random.randint(0, WIDTH - 250)
        self.dvd_y = random.randint(0, HEIGHT - 150)
        self.dvd_speed_x = 3
        self.dvd_speed_y = 3
        self.current_dvd_image = 0
        self.total_hits = 0
        self.credits_sequence = False
        self.credits_alpha = 0

    def clear_entities(self):
        """Clear all entities from the game."""
        self.entities.clear()
        self.projectiles.clear()
        self.boxes.clear()

    def draw_game_over(self):
        """Draw the game over screen."""
        screen.fill((0, 0, 0))
        if self.victory:  # Victory condition
            text = font.render("Victory!", True, (0, 255, 0))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
            # Draw a smiley face
            pygame.draw.circle(screen, (255, 255, 0), (WIDTH // 2, HEIGHT // 2 + 50), 50)
            pygame.draw.circle(screen, (0, 0, 0), (WIDTH // 2 - 20, HEIGHT // 2 + 30), 10)
            pygame.draw.circle(screen, (0, 0, 0), (WIDTH // 2 + 20, HEIGHT // 2 + 30), 10)
            pygame.draw.arc(screen, (0, 0, 0), (WIDTH // 2 - 30, HEIGHT // 2 + 50, 60, 40), math.pi, 2 * math.pi, 5)
        else:
            text = font.render("Game Over", True, (255, 0, 0))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))


class MenuSystem:
    def __init__(self):
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        button_width = 300
        button_height = 60
        spacing = 20
        start_y = HEIGHT // 2 - 100

        self.buttons = [
            Button("Falling Shapes", (WIDTH // 2 - button_width // 2, start_y),
                   button_width, button_height, self.start_falling_shapes),
            Button("Box Breaker", (WIDTH // 2 - button_width // 2, start_y + button_height + spacing),
                   button_width, button_height, self.start_box_breaker),
            Button("DVD Bounce", (WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + spacing)),
                   button_width, button_height, self.start_dvd_bounce),
            Button("Quit", (WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + spacing)),
                   button_width, button_height, self.quit_game)
        ]
    if not is_menu_music_playing:
        menu_music.play(-1)
        is_menu_music_playing = True

    def draw(self):
        screen.fill((30, 30, 50))
        title = font.render("WELCOME! ", True, (255, 255, 200))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        for button in self.buttons:
            button.draw(screen)

    def start_falling_shapes(self):
        global current_game
        current_game = FALLING_SHAPES
        game_manager.clear_entities()

    def start_box_breaker(self):
        global current_game
        current_game = BOX_BREAKER
        game_manager.clear_entities()
        game_manager.create_level()

    def start_dvd_bounce(self):
        global current_game
        current_game = BOUNCING_DVD
        game_manager.clear_entities()
        game_manager.init_dvd()

    def quit_game(self):
        pygame.quit()
        exit()


class Button:
    def __init__(self, text, pos, width, height, callback):
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.text = text
        self.callback = callback
        self.normal_color = (80, 80, 120)
        self.hover_color = (120, 120, 180)

    def draw(self, surface):
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.normal_color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_surf = small_font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()


# Initialize systems
game_manager = GameManager()
menu_system = MenuSystem()

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_game == MENU:
                for button in menu_system.buttons:
                    button.handle_click(event.pos)
            elif current_game == FALLING_SHAPES:
                if event.button == 3:  # Правый клик
                    game_manager.spawn_random_entity()
            elif current_game == BOX_BREAKER:
                if event.button == 1:
                    game_manager.start_drag(event.pos)
            elif current_game == BOUNCING_DVD:
                # Проверяем, если нажали на ползунок
                if (game_manager.slider_x <= event.pos[0] <= game_manager.slider_x + game_manager.slider_width and
                        game_manager.slider_y <= event.pos[1] <= game_manager.slider_y + game_manager.slider_height):
                    game_manager.slider_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if current_game == BOX_BREAKER:
                if event.button == 1:
                    game_manager.end_drag(event.pos)
            elif current_game == BOUNCING_DVD:
                game_manager.slider_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if current_game == BOUNCING_DVD and game_manager.slider_dragging:
                game_manager.update_slider(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_manager.game_over or game_manager.victory or game_manager.credits_sequence:  # Если игра завершена, возвращаемся в меню
                    current_game = MENU
                    game_manager.reset_game()  # Сбрасываем состояние игры
                else:
                    current_game = MENU
                    game_manager.clear_entities()
            elif event.key == pygame.K_p:
                game_manager.paused = not game_manager.paused
            elif event.key == pygame.K_r:
                game_manager.clear_entities()

    if current_game == MENU:
        menu_system.draw()
    elif current_game == FALLING_SHAPES:
        game_manager.update_entities(current_game)
        font = pygame.font.Font(None, 25)
        text = font.render("RBM - creates new balls", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        text = font.render("P - stop time", True, (255, 255, 255))
        screen.blit(text, (10, 35))
        text = font.render("R - remove all balls", True, (255, 255, 255))
        screen.blit(text, (10, 60))

        for entity in game_manager.entities:
            entity.draw()
    elif current_game == BOX_BREAKER:
        game_manager.update_entities(current_game)
        game_manager.draw_aim()
        for box in game_manager.boxes:
            box.draw()
        for projectile in game_manager.projectiles:
            projectile.draw()
        # display score and time
        score_text = small_font.render(f"Score: {game_manager.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        timer_text = small_font.render(f"Time: {int(game_manager.time_left)}", True, (255, 255, 255))
        screen.blit(timer_text, (WIDTH - 150, 10))
    elif current_game == BOUNCING_DVD:
        game_manager.update_dvd()
        game_manager.draw_dvd()
        game_manager.draw_counters()
        game_manager.draw_credits()
        game_manager.draw_slider()

    if game_manager.game_over:
        game_manager.draw_game_over()



    if current_game == MENU:
        if not is_menu_music_playing:
            menu_music.play(-1)
            is_menu_music_playing = True

    else:
        if is_menu_music_playing:
            menu_music.stop()
            is_menu_music_playing = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()