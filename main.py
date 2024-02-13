import uuid
import pickle

from fastapi import FastAPI

from src import models
from src.cors import configure_cors
from src.config import PATH_TO_DATA
from src.http_handlers import handler400
from src.utils import generate_empty_field, set_mines_on_field, mkdir_if_not_exists, gameid_is_exists, \
    get_number_of_neighbors, open_all_possible_neighbors


app = FastAPI()
configure_cors(app)


@app.post("/api/new")
async def new(params: models.ParametersNewGame):
    game_id = uuid.uuid4()
    width = params.width
    height = params.height
    mines_count = params.mines_count
    path = f'{PATH_TO_DATA}/{game_id}.pickle'

    if not 2 <= width <= 30:
        return handler400('ширина поля должна быть не менее 2 и не более 30')
    if not 2 <= height <= 30:
        return handler400('высота поля должна быть не менее 2 и не более 30')
    if mines_count >= width * height:
        return handler400(f'количество мин должно быть не менее 1 и не более {width * height - 1}')

    # Генерируем пустое игровое поле
    field = generate_empty_field(width, height)
    mines = set_mines_on_field(width, height, mines_count)

    # Сериализуем игровое поле для использования при последующих запросах
    mkdir_if_not_exists(PATH_TO_DATA)
    with open(path, 'wb') as f:
        pickle.dump(models.GameField(
            game_id=game_id, field=field, width=width, height=height,
            mines_count=mines_count, mines=mines, checked_cells=set(), completed=False
        ), f)

    return models.Response(
        game_id=game_id, width=width, height=height,
        mines_count=mines_count, completed=False, field=field
    )


@app.post('/api/turn')
async def turn(params: models.ParametersMove):
    col = params.col
    row = params.row
    game_id = params.game_id
    path = f'{PATH_TO_DATA}/{game_id}.pickle'

    if not gameid_is_exists(path):
        return handler400(f'игра с идентификатором {game_id} не была создана или устарела (неактуальна)')

    # Восстанавливаем состояние игры
    with open(path, 'rb') as f:
        gamefield = pickle.load(f)

    # Если игра завершена или если кликнули по уже открытой ячейке,
    # необходимо вернуть статус-код 400 с текстовым описанием ошибки
    if gamefield.completed:
        return handler400('игра завершена')
    if (row, col) in gamefield.checked_cells:
        return handler400('уже открытая ячейка')

    # По условию задачи при попадании на бомбу нужно:
    #  - заменить все бомбы на 'X';
    #  - открыть все остальные ячейки;
    #  - прекратить игру.
    if (row, col) in gamefield.mines:
        for row_index, row_value in enumerate(gamefield.field):
            for col_index, col_value in enumerate(row_value):
                if (row_index, col_index) in gamefield.mines:
                    new_value = 'X'
                else:
                    new_value = get_number_of_neighbors(row_index, col_index, gamefield)
                gamefield.field[row_index][col_index] = new_value
                gamefield.checked_cells.add((row_index, col_index))
        gamefield.completed = True

        with open(path, 'wb') as f:
            pickle.dump(gamefield, f)

        return models.Response(
            game_id=game_id, width=gamefield.width, height=gamefield.height,
            mines_count=gamefield.mines_count, completed=True, field=gamefield.field
        )

    # Для ячеек, у которых нет соседей с бомбами, открываем не только саму ячейку, а несколько соседних.
    number_of_neighbors = get_number_of_neighbors(row, col, gamefield)
    if number_of_neighbors == 0:
        open_all_possible_neighbors(row, col, gamefield)
    else:
        gamefield.field[row][col] = number_of_neighbors
        gamefield.checked_cells.add((row, col))

    # Если открыты все ячейки и остались неоткрыты только бомбы,
    # то по условию задачи заменяем все 'X' на 'M' и возвращаем полностью открытое поле
    if len(gamefield.mines) + len(gamefield.checked_cells) == gamefield.height * gamefield.width:
        completed = True
        gamefield.completed = True
        for row, col in gamefield.mines:
            gamefield.field[row][col] = 'M'
    else:
        completed = False
        gamefield.completed = False

    # Сериализуем изменения на диск
    with open(path, 'wb') as f:
        pickle.dump(gamefield, f)

    return models.Response(
        game_id=game_id, width=gamefield.width, height=gamefield.height,
        mines_count=gamefield.mines_count, completed=completed, field=gamefield.field
    )
