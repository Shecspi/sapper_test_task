from fastapi.responses import JSONResponse


def handler400(message: str) -> JSONResponse:
    """
    Генерирует JSON-ответ со статус-кодом 400.
    :param message: Сообщение, которое должно быть возвращено вместе с ответом
    """
    return JSONResponse(status_code=400, content={'error': message})
