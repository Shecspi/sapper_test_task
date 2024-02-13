import random
from pathlib import Path
from typing import Literal, TypeAlias

from src.models import GameField


CellValues: TypeAlias = Literal[' ', 'X', 'M'] | int
MinesSet: TypeAlias = set[tuple[int, int]]


def mkdir_if_not_exists(path: str) -> None:
    """
    Создаёт директорию для хранения файлов игры, если она ещё не существует.
    :param path: Путь, по которому необходимо создать директорию.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def gameid_is_exists(path: str) -> bool:
    """
    Проверяет, существует ли указанный файл.
    :param path: Путь к файлу.
    :return: True, если файл существует, иначе False.
    """
    return Path(path).is_file()


def generate_empty_field(width: int, height: int) -> list[list[CellValues]]:
    """
    Создаёт новое пустое поле.
    :param width: Ширина игрового поля.
    :param height: Высота игрового поля.
    :return: Созданное игровое поле
    """
    field = [[' ' for _ in range(width)] for _ in range(height)]

    return field


def set_mines_on_field(width: int, height: int, mines_count: int) -> MinesSet:
    """
    Создаёт множество, в котором перечислены координаты мин.
    :param width: Ширина игрового поля.
    :param height: Высота игрового поля.
    :param mines_count: Количество мин, которое необходимо установить.
    :return: Множество с координатами ячеек, в которых установлены бомбы.
    """
    mines = set()

    while len(mines) < mines_count:
        random_width = random.randint(0, width - 1)
        random_heiht = random.randint(0, height - 1)

        if (random_heiht, random_width) not in mines:
            mines.add((random_heiht, random_width))

    return mines


def get_number_of_neighbors(row: int, col: int, gamefield: GameField) -> int:
    """
    Проверяет количество бомб вокруг указанной клетки.
    :param row: Координата Y порверяемой клетки.
    :param col: Координата X проверяемой клетки.
    :param gamefield: Игровое поле
    :return: Количество бомб, находящихся на соседних клетках.
    """
    number_of_bombs = 0

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            # Саму клетку нет смысла проверять
            if dx == 0 and dy == 0:
                continue

            position_x = col + dx
            position_y = row + dy
            if 0 <= position_y < gamefield.height and 0 <= position_x < gamefield.width:
                if (position_y, position_x) in gamefield.mines:
                    number_of_bombs += 1

    return number_of_bombs


def open_all_possible_neighbors(row: int, col: int, gamefield: GameField) -> None:
    """
    Открывает все соседние ячейки, у которых нет соседей с бомбой,
    а также обрамляющие их целочисленные ячейки.
    :param row: Координата Y порверяемой клетки.
    :param col: Координата X порверяемой клетки.
    :param gamefield: Игровое поле
    """
    queue = [(row, col)]
    is_checked = set()

    while queue:
        current_y, current_x = queue.pop()

        if (current_y, current_x) in is_checked:
            continue

        # Добавляем клетку во множество проверенных клеток, чтобы не допустить бесконечного цикла
        is_checked.add((current_y, current_x))

        # Проверяем только 4 соседние клетки слева/справа/сверху/снизу
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            position_y = current_y + dy
            position_x = current_x + dx

            if 0 <= position_y < len(gamefield.field) and 0 <= position_x < len(gamefield.field[0]):
                number = get_number_of_neighbors(position_y, position_x, gamefield)
                gamefield.field[position_y][position_x] = number
                gamefield.checked_cells.add((position_y, position_x))

                # Если у клетки нет соседей-бомб, то добавляем её в очередь для проверки её соседей
                if number == 0:
                    queue.append((position_y, position_x))
