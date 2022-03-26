import pygame
import collections

colors = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "wooden": (153, 92, 0, 255),
}


class ScreenHandle(pygame.Surface):
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def draw(self, canvas):
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self, engine):
        if self.successor is not None:
            self.successor.connect_engine(engine)


class MiniMap(ScreenHandle):
    tile = 4

    def connect_engine(self, engine):
        self.game_engine = engine
        super().connect_engine(engine)

    def draw_hero(self):
        self.draw_object(self.game_engine.hero.sprite[1], self.game_engine.hero.position)

    def draw_map(self):
        self.fill(colors["wooden"])

        min_x = 0
        min_y = 0

        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - min_x):
                for j in range(len(self.game_engine.map) - min_y):
                    self.blit(self.game_engine.map[min_y + j][min_x + i][
                                  0][1], (i * self.tile, j * self.tile))
        else:
            self.fill(colors["white"])

    def draw_object(self, sprite, coord):
        size = self.tile

        min_x = 0
        min_y = 0

        self.blit(sprite, ((coord[0] - min_x) * size,
                           (coord[1] - min_y) * size))

    def draw(self, canvas):
        size = self.tile

        min_x = 0
        min_y = 0

        self.draw_map()
        for obj in self.game_engine.objects:
            self.blit(obj.sprite[0][1], ((obj.position[0] - min_x) * size,
                                         (obj.position[1] - min_y) * size))
        self.draw_hero()
        super().draw(canvas)


class GameSurface(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super(GameSurface, self).__init__(*args, **kwargs)
        self.min_x = 0
        self.min_y = 0

    def connect_engine(self, engine):
        self.game_engine = engine
        super().connect_engine(engine)

    def draw_hero(self):
        self.draw_object(self.game_engine.hero.sprite, self.game_engine.hero.position)

    def draw_map(self):
        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - self.min_x):
                for j in range(len(self.game_engine.map) - self.min_y):
                    self.blit(self.game_engine.map[self.min_y + j][self.min_x + i][
                                  0][0], (i * self.game_engine.sprite_size, j * self.game_engine.sprite_size))
        else:
            self.fill(colors["white"])

    def draw_object(self, sprite, coord):
        self.blit(sprite[0], ((coord[0] - self.min_x) * self.game_engine.sprite_size,
                              (coord[1] - self.min_y) * self.game_engine.sprite_size))

    def draw(self, canvas):
        size = self.game_engine.sprite_size
        self.fill(colors["wooden"])

        screen = 640, 480
        edge = 100
        while (self.game_engine.hero.position[0] - self.min_x) * size > screen[0] - edge:
            self.min_x += 1
        while (self.game_engine.hero.position[0] - self.min_x) * size < edge:
            self.min_x -= 1
        while (self.game_engine.hero.position[1] - self.min_y) * size > screen[1] - edge:
            self.min_y += 1
        while (self.game_engine.hero.position[1] - self.min_y) * size < edge:
            self.min_y -= 1

        self.draw_map()
        for obj in self.game_engine.objects:
            self.blit(obj.sprite[0][0], ((obj.position[0] - self.min_x) * self.game_engine.sprite_size,
                                         (obj.position[1] - self.min_y) * self.game_engine.sprite_size))
        self.draw_hero()
        super().draw(canvas)


class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(colors["wooden"])

    def connect_engine(self, engine):
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        self.fill(colors["wooden"])
        pygame.draw.rect(self, colors["black"], (50, 30, 200, 30), 2)
        pygame.draw.rect(self, colors["black"], (50, 70, 200, 30), 2)

        pygame.draw.rect(self, colors[
            "red"], (50, 30, 200 * min(self.engine.hero.hp / self.engine.hero.max_hp, 1), 30))
        pygame.draw.rect(self, colors["green"], (50, 70,
                                                 200 * self.engine.hero.exp / (
                                                         100 * (2 ** (self.engine.hero.level - 1))), 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, colors["black"]),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level} floor', True, colors["black"]),
                  (10, 0))

        self.blit(font.render(f'HP', True, colors["black"]),
                  (10, 30))
        self.blit(font.render(f'Exp', True, colors["black"]),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, colors["black"]),
                  (60, 30))
        self.blit(
            font.render(f'{self.engine.hero.exp}/{(100 * (2 ** (self.engine.hero.level - 1)))}', True, colors["black"]),
            (60, 70))

        self.blit(font.render(f'Level', True, colors["black"]),
                  (300, 30))
        self.blit(font.render(f'Gold', True, colors["black"]),
                  (300, 70))

        self.blit(font.render(f'{self.engine.hero.level}', True, colors["black"]),
                  (360, 30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, colors["black"]),
                  (360, 70))

        self.blit(font.render(f'Str', True, colors["black"]),
                  (420, 30))
        self.blit(font.render(f'Luck', True, colors["black"]),
                  (420, 70))

        self.blit(font.render(f'{self.engine.hero.stats["strength"]}', True, colors["black"]),
                  (480, 30))
        self.blit(font.render(f'{self.engine.hero.stats["luck"]}', True, colors["black"]),
                  (480, 70))

        self.blit(font.render(f'SCORE', True, colors["black"]),
                  (550, 30))
        self.blit(font.render(f'{self.engine.score:.4f}', True, colors["black"]),
                  (550, 70))
        super().draw(canvas)


class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill(colors["wooden"])
        self.get_size()

        font = pygame.font.SysFont("comicsansms", 10)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, colors["black"]),
                      (5, 20 + 18 * i))
        super().draw(canvas)

    # draw next surface in chain

    def connect_engine(self, engine):  # set this class as Observer to engine and send it to next in
        # self.engine = engine
        engine.subscribe(self)
        super().connect_engine(engine)


class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append(["D, →", "Move Right"])
        self.data.append(["A, ←", "Move Left"])
        self.data.append(["W, ↑ ", "Move Top"])
        self.data.append(["S, ↓ ", "Move Bottom"])
        self.data.append(["F1, H", "Show Help"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])
        self.data.append(["Esc", "Quit Game"])

    def connect_engine(self, engine):  # save engine and send it to next in chain
        self.engine = engine
        super().connect_engine(engine)

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, (128, 128, 255)),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, (128, 128, 255)),
                          (150, 50 + 30 * i))

        super().draw(canvas)
    # draw next surface in chain
