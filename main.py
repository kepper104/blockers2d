import pygame
import noise
import os
import sys
from random import randint

block_colors = {"grass": (27, 72, 10), "stone": (60, 63, 65), "dirt": (48, 30, 13)}
pygame.init()

block_size = 32
# texture res
screen_width = 1920
screen_height = 1056
world_size = screen_width // block_size
isGrassing = True
current_mode = "Mode: Dig"
game_world = None
all_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()

def load_image(name, colorkey=None):
    fullname = os.path.join('sprites', name)
    if not os.path.isfile(fullname):
        print(f"File '{fullname}' not found")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Block:
    def __init__(self, block_type, x, y, size):
        self.block_type = block_type
        self.x = x
        self.y = y
        self.size = size
        self.sprite = pygame.sprite.Sprite(all_sprites)
        # print("Added", all_sprites)
        self.sprite.image = load_image(self.block_type + ".png")

        self.sprite.rect = self.sprite.image.get_rect()

    def draw(self):
        self.sprite.image = load_image(self.block_type + ".png")
        self.sprite.rect.x = self.x * block_size
        self.sprite.rect.y = self.y * block_size

        # pygame.draw.rect(surface, block_colors[self.block_type],
        #                  (self.x * block_size, self.y * block_size, self.size, self.size))

    def kill_sprite(self):
        self.sprite.kill()

class Player:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.sprite = pygame.sprite.Sprite(player_sprite)
        self.sprite.image = load_image("player.png")
        self.sprite.rect = self.sprite.image.get_rect()

    def draw(self):
        self.sprite.rect.x = self.x * block_size
        self.sprite.rect.y = self.y * block_size
        # pygame.draw.rect(surface, (255, 100, 0), (self.x * block_size, self.y * block_size, self.size, self.size))

    def __str__(self):
        return f"{self.x}, {self.y}"

    def move(self, direction):
        if direction == "right":
            if game_world[self.x + 1][self.y] is None:
                game_world[self.x][self.y] = None
                self.x += 1
                game_world[self.x][self.y] = self

            elif game_world[self.x + 1][self.y] is not None and game_world[self.x + 1][self.y - 1] is None and \
                    game_world[self.x][self.y - 1] is None:
                game_world[self.x][self.y] = None
                self.x += 1
                self.y -= 1
                game_world[self.x][self.y] = self

        elif direction == "left":
            if game_world[self.x - 1][self.y] is None:
                game_world[self.x][self.y] = None
                self.x -= 1
                game_world[self.x][self.y] = self

            elif game_world[self.x - 1][self.y] is not None and game_world[self.x - 1][self.y - 1] is None and \
                    game_world[self.x][self.y - 1] is None:
                game_world[self.x][self.y] = None
                self.x -= 1
                self.y -= 1
                game_world[self.x][self.y] = self

        # elif direction == "jump":
        #     if game_world[self.x][self.y + 1] is not None:
        #         game_world[self.x][self.y] = None
        #         self.y -= 5
        #         game_world[self.x][self.y] = self

        elif direction == "down":
            game_world[self.x][self.y] = None
            self.y += 1
            game_world[self.x][self.y] = self

    def interact(self, x, y):
        if self.x == x and self.y == y:
            return
        if abs(self.x - x) <= 2 and abs(self.y - y) <= 2:
            if current_mode == "Mode: Dig":
                self._dig(x, y)
            elif current_mode == "Mode: Place":
                self._place(x, y)

    def _dig(self, x, y):
        print(f"MINE: {x}, {y}")
        if game_world[x][y]:
            game_world[x][y].kill_sprite()
            game_world[x][y] = None

    def _place(self, x, y):
        print(f"PLACE: {x}, {y}")
        if game_world[x][y] is None:
            game_world[x][y] = Block("stone", x, y, block_size)


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


def main():
    global game_world, current_mode

    font = pygame.font.Font(pygame.font.get_default_font(), 40)

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Blockers 2D")

    world_width = screen_width // block_size
    world_height = screen_height // block_size

    game_world = [[None for y in range(world_height)] for x in range(world_size)]

    noise_map_surface = generate_noise_map(world_size, 5, 1, 0.5, 2, randint(0, 100))
    noise_map_stone = generate_noise_map(world_size, 5, 1, 0.5, 2, randint(0, 100))

    for x in range(world_size):
        noise_value = noise_map_surface[x]
        res_y = int(noise_value * 5) + 20
        # game_world[x][res_y] = Block("dirt", x, res_y, block_size)
        for y in range(world_height):
            if y >= res_y:
                game_world[x][y] = Block("dirt", x, y, block_size)

    for x in range(world_size):
        noise_value = noise_map_stone[x]
        res_y = int(noise_value * 5) + 30
        # game_world[x][res_y] = Block("stone", x, res_y, block_size)
        for y in range(world_height):
            if y >= res_y:
                game_world[x][y] = Block("stone", x, y, block_size)

    # spawning player
    player = Player(2, 2, block_size)
    game_world[2][2] = player

    running = True
    clock = pygame.time.Clock()

    # populating top layer with grass
    for x in range(world_width):
        for y in range(1, world_height):
            if game_world[x][y - 1] is None and game_world[x][y] is not None and isGrassing:
                game_world[x][y].block_type = "grass"

    label_mode = font.render(current_mode, 1, (255, 0, 0))
    label_instruction1 = font.render("Press Space to Change Mode!", 1, (255, 0, 0))
    label_instruction2 = font.render("Use WASD to walk around!", 1, (255, 0, 0))
    label_instruction3 = font.render("Use your mouse to interact with environment!", 1, (255, 0, 0))

    # count = 0
    # for i in game_world:
    #     for j in i:
    #         if j is not None:
    #             count += 1
    # print("COUNT:", count)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
                    # print("SPACED!", current_mode)
                    label_mode = font.render(current_mode, 1, (255, 0, 0))

            elif event.type == pygame.MOUSEBUTTONUP:
                player.interact(event.pos[0] // block_size, event.pos[1] // block_size)

        screen.fill((26, 179, 255))
        screen.blit(label_mode, (40, 10))
        screen.blit(label_instruction1, (40, 60))
        screen.blit(label_instruction2, (1000, 10))
        screen.blit(label_instruction3, (1000, 50))

        if game_world[player.x][player.y + 1] is None:
            player.move("down")

        for x in range(world_width):
            for y in range(world_height):
                object = game_world[x][y]
                if object:
                    object.draw()

        all_sprites.draw(screen)
        player_sprite.draw(screen)
        clock.tick(10)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

