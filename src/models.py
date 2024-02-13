import uuid
from dataclasses import dataclass

from pydantic import BaseModel


class ParametersNewGame(BaseModel):
    """
    Модельь Pydantic, используемая для создания нового игрового поля.
    """
    width: int
    height: int
    mines_count: int


class ParametersMove(BaseModel):
    """
    Модель Pydantic, используемая для изменения игрового поля на основе выбранной пользователем ячейки.
    """
    game_id: uuid.UUID
    col: int
    row: int


class Response(BaseModel):
    """
    Модель Pydantic для ответа пользователю на его действия.
    """
    game_id: uuid.UUID
    width: int
    height: int
    mines_count: int
    completed: bool
    field: list[list]


@dataclass
class GameField:
    """
    Структура для хранения всей информации о состоянии поля
    """
    game_id: uuid.UUID
    field: list[list]
    width: int
    height: int
    mines_count: int
    mines: set[tuple[int, int]]
    checked_cells: set[tuple[int, int] | None]
    completed: bool
