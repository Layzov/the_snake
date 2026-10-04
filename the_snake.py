from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет "неправильной" еды
BAD_FOOD_COLOR = (160, 32, 240)

# Цвет камня
STONE_COLOR = (128, 128, 128)

# Скорость движения змейки:
SPEED = 5

# Максимальная скорость змейки:
MAX_SPEED = 25

# Центр игрового поля:
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


def get_random_position(occupied_positions=()):
    """Возвращает случайную клетку поля, не входящую в occupied_positions."""
    while True:
        position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )
        if position not in occupied_positions:
            return position


class GameObject:
    """Базовый класс для всех объектов игрового поля."""

    def __init__(self, position=SCREEN_CENTER, body_color=None):
        """Задаёт позицию и цвет объекта.

        По умолчанию объект находится в центре игрового поля.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на игровом поле.

        Метод-заготовка: переопределяется в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Яблоко: появляется в случайной клетке игрового поля."""

    def __init__(self, occupied_positions=()):
        """Задаёт цвет яблока и выбирает для него случайную клетку.

        occupied_positions - клетки, на которых яблоко появляться не должно.
        """
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбирает новую случайную позицию яблока в пределах поля.

        Позиция не совпадает с клетками из occupied_positions
        (например, с телом змейки).
        """
        self.position = get_random_position(occupied_positions)

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class BadFood(Apple):
    """Неправильная еда: при поедании змейка становится короче."""

    def __init__(self, occupied_positions=()):
        """Задаёт цвет неправильной еды и выбирает для неё клетку."""
        super().__init__(occupied_positions)
        self.body_color = BAD_FOOD_COLOR


class Stone(GameObject):
    """Камень: при столкновении с ним игра начинается заново."""

    def __init__(self, occupied_positions=()):
        """Задаёт цвет камня и выбирает для него случайную клетку."""
        super().__init__(body_color=STONE_COLOR)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбирает новую случайную позицию камня в пределах поля."""
        self.position = get_random_position(occupied_positions)

    def draw(self):
        """Отрисовывает камень на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка: хранит сегменты тела, двигается и растёт."""

    def __init__(self):
        """Создаёт змейку длиной 1 в центре поля, движущуюся вправо."""
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения после нажатия на клавишу."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """Сдвигает змейку на одну клетку в текущем направлении.

        Новая голова добавляется в начало списка positions, последний
        сегмент удаляется, если змейка не выросла. При выходе за край
        поля змейка появляется с противоположной стороны.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def shrink(self):
        """Укорачивает змейку на один сегмент (но не короче одной клетки)."""
        if self.length > 1:
            self.length -= 1
            removed = self.positions.pop()
            rect = pygame.Rect(removed, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

    def draw(self):
        """Отрисовывает змейку и затирает след от хвоста."""
        # Отрисовка тела змейки (без головы)
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Возвращает змейку в начальное состояние.

        Длина становится 1, голова - в центре поля, направление
        выбирается случайно.
        """
        self.length = 1
        self.positions = [SCREEN_CENTER]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и закрытие окна.

    Стрелки меняют направление змейки, но развернуться на 180 градусов
    нельзя.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Запускает игру и основной игровой цикл."""
    # Инициализация PyGame:
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    bad_food = BadFood(snake.positions + [apple.position])
    stone = Stone(snake.positions + [apple.position, bad_food.position])

    while True:
        clock.tick(min(SPEED + snake.length - 1, MAX_SPEED))

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()
        occupied = snake.positions + [
            apple.position, bad_food.position, stone.position
        ]
        # Змейка съела яблоко:
        if head == apple.position:
            snake.length += 1
            apple.randomize_position(occupied)
        # Змейка съела "неправильную" еду:
        elif head == bad_food.position:
            snake.shrink()
            bad_food.randomize_position(occupied)
        # Змейка врезалась в себя или в камень:
        elif head in snake.positions[1:] or head == stone.position:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
            bad_food.randomize_position(snake.positions + [apple.position])
            stone.randomize_position(
                snake.positions + [apple.position, bad_food.position]
            )

        apple.draw()
        bad_food.draw()
        stone.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()