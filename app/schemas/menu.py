from pydantic import BaseModel, Field


class MenuBase(BaseModel):
    title: str = Field(max_length=20)
    description: str | None = Field(default=None, max_length=150)


class MenuPublic(MenuBase):
    menu_id: int


class MenuUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=150)
