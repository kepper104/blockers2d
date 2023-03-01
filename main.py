import pygame
import noise


block_colors = {"grass": (27, 72, 10), "stone": (60, 63, 65), "dirt": (48, 30, 13)}
block_size = 32
# texture res
screen_width = 1920
screen_height = 1080
isGrassing = True
current_mode = "dig"

game_world = []

class Block:
    def __init__(self, block_type, x, y, size):
        self.block_type = block_type
        self.x = x
        self.y = y
        self.size = size

    def draw(self, surface):
        pygame.draw.rect(surface, block_colors[self.block_type],
                         (self.x * block_size, self.y * block_size, self.size, self.size))


class Player:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 100, 0), (self.x * block_size, self.y * block_size, self.size, self.size))

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

    def dig(self, direction):
        if direction == "right":
            game_world[self.x + 1][self.y] = None

        elif direction == "left":
            game_world[self.x - 1][self.y] = None

        elif direction == "up":
            game_world[self.x][self.y - 1] = None

        elif direction == "down":
            game_world[self.x][self.y + 1] = None

        elif direction == "leftup":
            game_world[self.x - 1][self.y - 1] = None

        elif direction == "rightup":
            game_world[self.x + 1][self.y - 1] = None



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
    pygame.init()

    # dig or place

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Blockers 2D")


    world_width = screen_width // 10
    world_height = screen_height // 10
    game_world = [[None for y in range(world_height)] for x in range(world_width)]

    noise_map = generate_noise_map(world_width, 10, 1, 0.5, 2, 0)

    for x in range(world_width):
        noise_value = noise_map[x]
        res_y = int(noise_value * 5) + 20
        game_world[x][res_y] = Block("dirt", x, res_y, block_size)
        for y in range(world_height):
            if y > int(noise_value * 5) + 20:
                game_world[x][y] = Block("dirt", x, y, block_size)





    player = Player(2, 2, block_size)

    # spawning player
    game_world[2][2] = player


    running = True
    clock = pygame.time.Clock()

    for x in range(world_width):
        for y in range(1, world_height):
            if game_world[x][y - 1] is None and game_world[x][y] is not None and isGrassing:
                game_world[x][y].block_type = "grass"


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move("left")
                elif event.key == pygame.K_RIGHT:
                    player.move("right")

                # elif event.key == pygame.K_UP:
                #     player.move("jump")

                elif event.key == pygame.K_w:
                    player.dig("up")

                elif event.key == pygame.K_a:
                    player.dig("left")

                elif event.key == pygame.K_s:
                    player.dig("down")

                elif event.key == pygame.K_d:
                    player.dig("right")

                elif event.key == pygame.K_q:
                    player.dig("leftup")

                elif event.key == pygame.K_e:
                    player.dig("rightup")

                elif event.key == pygame.K_SPACE:
                    if current_mode == "dig":
                        current_mode = "place"
                    else:
                        current_mode = "place"

        screen.fill((26, 179, 255))
        if game_world[player.x][player.y + 1] is None:
            player.move("down")

        for x in range(world_width):
            for y in range(world_height):
                object = game_world[x][y]
                if object:
                    object.draw(screen)

        # player.draw(screen)

        clock.tick(10)
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()