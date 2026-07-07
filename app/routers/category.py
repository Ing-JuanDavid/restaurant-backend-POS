# from fastapi import APIRouter, HTTPException, status
# from app.database import SessionDep
# from app.models import *
# from sqlmodel import select


# router = APIRouter(
#     prefix="/category",
#     tags=["category"]
# )


# @router.get("", response_model=list[PublicCategory])
# async def read_categories(session: SessionDep):

#     categories = session.exec(select(Category)).all()
#     return categories


# @router.post("", response_model=PublicCategory)
# async def create_category(category: BaseCategory, session: SessionDep):
#     db_category = Category.model_validate(category)

#     session.add(db_category)
#     session.commit()
#     session.refresh(db_category)

#     return db_category


# @router.put("/{category_id}", response_model=PublicCategory)
# async def update_category(category_id: int, category: BaseCategory, session: SessionDep):
#     db_category = session.get(Category, category_id)

#     if not db_category:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Category not found"
#         )

#     category_data = category.model_dump()
#     db_category.sqlmodel_update(category_data)
#     session.add(db_category)
#     session.commit()
#     session.refresh(db_category)

#     return db_category


# @router.delete("/{category_id}")
# async def delete_category(category_id: int, session: SessionDep):
#     db_category = session.get(Category, category_id)

#     if not db_category:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Category not found"
#         )

#     session.delete(db_category)
#     session.commit()

#     return {"message": "ok"}


# @router.get("/{category_id}/items")
# async def read_category_items(category_id: int, session: SessionDep):

#     db_category = session.get(Category, category_id)

#     if not db_category:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Category not found"
#         )

#     statement = select(MenuItem).where(MenuItem.category_id == category_id)
#     items = session.exec(statement).all()

#     return items
