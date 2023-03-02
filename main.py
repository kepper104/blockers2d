import os
import sys
from random import randint

try:
    import pygame
    import noise
except ModuleNotFoundError:
    import setup

    print("All missing Packages were installed, please restart the program now")
    exit(0)

# Colors
BLUE_SKY = (26, 179, 255)
GRASS_BLOCK = (27, 72, 10)
STONE_BLOCK = (60, 63, 65)
DIRT_BLOCK = (60, 63, 65)

# Used when Blocks didn't have textures
block_colors = {"grass": GRASS_BLOCK, "stone": STONE_BLOCK, "dirt": DIRT_BLOCK}

pygame.init()  # I hate this

BLOCK_SIZE = 32  # Texture resolution

WINDOW_WIDTH = pygame.display.Info().current_w // BLOCK_SIZE * BLOCK_SIZE
WINDOW_HEIGHT = pygame.display.Info().current_h // BLOCK_SIZE * BLOCK_SIZE

FONT_SIZE = WINDOW_WIDTH // 50
FPS = 60
SEED = randint(0, 20)
WORLD_SIZE = WINDOW_WIDTH // BLOCK_SIZE
NEW_GAME = False
SHOW_UI = True


world_width = WINDOW_WIDTH // BLOCK_SIZE
world_height = WINDOW_HEIGHT // BLOCK_SIZE

current_mode = "Mode: Dig"

all_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()


def close():
    pygame.quit()
    exit(0)


def generate_noise_map(width, scale, octaves, persistence, lacunarity, seed):
    noise_map = [0 for x in range(width)]

    for x in range(width):
        nx = x / width * scale
        value = 0
        for i in range(octaves):
            freq = 2 ** i
            amp = persistence ** i
            value += noise.snoise2((nx * freq) + seed, seed, octaves) * amp
        noise_map[x] = value

    return noise_map


def load_image(name):
    fullname = os.path.join('sprites', name)
    if not os.path.isfile(fullname):
        print(f"File '{fullname}' not found")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def save_game():
    with open("save.txt", "w") as f:
        save = ""
        for x in range(0, len(game_world[0])):
            line = ""

            for y in range(len(game_world)):
                j = game_world[y][x]
                if j is None:
                    line += "."
                elif isinstance(j, Player):
                    line += "P"
                elif j.block_type == "grass":
                    line += "G"
                elif j.block_type == "stone":
                    line += "S"
                elif j.block_type == "dirt":
                    line += "D"

            save += line + "\n"
        f.write(save)


def load_game():
    game_world = [[None for y in range(world_height)] for x in range(WORLD_SIZE)]
    player = None
    with open("save.txt", "r") as f:
        contents = f.readlines()
        for x in range(len(contents[0])):
            for y in range(len(contents)):
                block = contents[y][x]
                if block == ".":
                    game_world[x][y] = None
                elif block == "P":
                    player = Player(x, y, BLOCK_SIZE)
                    game_world[x][y] = player
                elif block == "G":
                    game_world[x][y] = Block("grass", x, y, BLOCK_SIZE)
                elif block == "D":
                    game_world[x][y] = Block("dirt", x, y, BLOCK_SIZE)
                elif block == "S":
                    game_world[x][y] = Block("stone", x, y, BLOCK_SIZE)

    return game_world, player


def place_block(x, y):
    print(f"PLACE: {x}, {y}")
    if game_world[x][y] is None:
        game_world[x][y] = Block("stone", x, y, BLOCK_SIZE)


def dig_block(x, y):
    print(f"MINE: {x}, {y}")
    if game_world[x][y]:
        game_world[x][y].kill_sprite()
        game_world[x][y] = None


class Block:
    def __init__(self, block_type, x, y, size):
        self.block_type = block_type
        self.x = x
        self.y = y
        self.size = size
        self.sprite = pygame.sprite.Sprite(all_sprites)
        self.sprite.image = load_image(self.block_type + ".png")
        self.sprite.rect = self.sprite.image.get_rect()

    def draw(self):
        # self.sprite.image = load_image(self.block_type + ".png")
        self.sprite.rect.x = self.x * BLOCK_SIZE
        self.sprite.rect.y = self.y * BLOCK_SIZE

        # pygame.draw.rect(surface, block_colors[self.block_type],
        #                  (self.x * block_size, self.y * block_size, self.size, self.size))

    def kill_sprite(self):
        self.sprite.kill()

    def __repr__(self):
        return self.block_type[0].capitalize()


class Player:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.sprite = pygame.sprite.Sprite(player_sprite)
        self.sprite.image = load_image("player.png")
        self.sprite.rect = self.sprite.image.get_rect()

    def draw(self):
        self.sprite.rect.x = self.x * BLOCK_SIZE
        self.sprite.rect.y = self.y * BLOCK_SIZE

        # pygame.draw.rect(surface, (255, 100, 0), (self.x * block_size, self.y * block_size, self.size, self.size))

    def __str__(self):
        return f"{self.x}, {self.y}"

    def move(self, direction):
        offset_x = 0
        offset_y = 0
        # Movement direction and checking move correctness
        if direction == "right":
            if game_world[self.x + 1][self.y] is None:
                offset_x = +1
                offset_y = 0

            elif game_world[self.x + 1][self.y] is not None and game_world[self.x + 1][self.y - 1] is None and \
                    game_world[self.x][self.y - 1] is None:
                offset_x = +1
                offset_y = -1

        elif direction == "left":
            if game_world[self.x - 1][self.y] is None:
                offset_x = -1

            elif game_world[self.x - 1][self.y] is not None and game_world[self.x - 1][self.y - 1] is None and \
                    game_world[self.x][self.y - 1] is None:
                offset_x = -1
                offset_y = -1
        if direction == "down":
            offset_y = +1
        game_world[self.x][self.y] = None
        self.x += offset_x
        self.y += offset_y
        game_world[self.x][self.y] = self

    def interact(self, x, y):
        if self.x == x and self.y == y:
            return
        if abs(self.x - x) <= 2 and abs(self.y - y) <= 2:
            if current_mode == "Mode: Dig":
                dig_block(x, y)
            elif current_mode == "Mode: Place":
                place_block(x, y)


def handle_event(event, player, font):
    global current_mode
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_a:
            player.move("left")
        elif event.key == pygame.K_d:
            player.move("right")

        elif event.key == pygame.K_SPACE:
            if current_mode == "Mode: Dig":
                current_mode = "Mode: Place"
            else:
                current_mode = "Mode: Dig"

        elif event.key == pygame.K_ESCAPE:
            close()
        elif event.key == pygame.K_TAB:
            save_game()
        elif event.key == pygame.K_l:
            load_game()
    elif event.type == pygame.MOUSEBUTTONUP:
        player.interact(event.pos[0] // BLOCK_SIZE, event.pos[1] // BLOCK_SIZE)
    label_mode = font.render(current_mode, 1, (255, 0, 0))

    return label_mode


def create_world():
    game_world = [[None for y in range(world_height)] for x in range(WORLD_SIZE)]
    noise_map_surface = generate_noise_map(WORLD_SIZE, 5, 1, 0.5, 2, SEED)
    noise_map_stone = generate_noise_map(WORLD_SIZE, 5, 1, 0.5, 2, SEED + 4)

    for x in range(WORLD_SIZE):
        noise_value = noise_map_surface[x]
        res_y = int(noise_value * 5) + 20
        for y in range(world_height):
            if y >= res_y:
                game_world[x][y] = Block("dirt", x, y, BLOCK_SIZE)

    for x in range(WORLD_SIZE):
        noise_value = noise_map_stone[x]
        res_y = int(noise_value * 5) + 30
        # game_world[x][res_y] = Block("stone", x, res_y, block_size)
        for y in range(world_height):
            if y >= res_y:
                game_world[x][y] = Block("stone", x, y, BLOCK_SIZE)

    # spawning player
    player = Player(2, 2, BLOCK_SIZE)
    game_world[2][2] = player

    # populating top layer with grass
    for x in range(world_width):
        for y in range(1, world_height - 1):
            if isinstance(game_world[x][y + 1], Block) and game_world[x][y] is None:
                if game_world[x][y + 1].block_type == "dirt":
                    game_world[x][y] = Block("grass", x, y, BLOCK_SIZE)
    return game_world, player


def draw_all(game_world, screen):
    for x in range(world_width):
        for y in range(world_height):
            object = game_world[x][y]
            if object:
                object.draw()

    all_sprites.draw(screen)
    player_sprite.draw(screen)


def main():
    global game_world, current_mode

    font = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Blockers 2D")

    if NEW_GAME:
        game_world, player = create_world()
    else:
        game_world, player = load_game()

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            label_mode = handle_event(event, player, font)

        screen.fill(BLUE_SKY)

        if SHOW_UI:
            label_mode = font.render(current_mode, 1, (255, 0, 0))
            label_instruction1 = font.render("Press Space to Change Mode!", 1, (255, 0, 0))
            label_instruction2 = font.render("Use A and D to walk around!", 1, (255, 0, 0))
            label_instruction3 = font.render("Use your mouse to interact with environment!", 1, (255, 0, 0))

            screen.blit(label_mode, (40, 10))
            screen.blit(label_instruction1, (40, 60))
            screen.blit(label_instruction2, (1000, 10))
            screen.blit(label_instruction3, (1000, 50))

        # Player Physics
        if game_world[player.x][player.y + 1] is None:
            player.move("down")

        draw_all(game_world, screen)

        clock.tick(FPS)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
