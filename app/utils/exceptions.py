from fastapi import HTTPException, status


def not_found(entity: str):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity} not found"
    )


def unauthorized(entity: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid {entity}"
    )


def invalid(entity: str):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"invalid {entity}"
    )


def not_available(entity: str):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{entity} is not available"
    )


def sale_paid():
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="sale already paid"
    )


def invalid_action(action: str):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{action}, invalid action"
    )


def opened_cash(cash_id: int):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"cash with id: {cash_id} already opened"
    )


def no_cash_opened():
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="no cash opened yet"
    )
