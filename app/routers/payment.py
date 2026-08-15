from fastapi import APIRouter


router = APIRouter(prefix="payments", tags=["payment"])


@router.post("")
