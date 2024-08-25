from sqlmodel import SQLModel as _SQLModel , Field, Relationship
from pydantic import EmailStr, UUID4, IPvAnyAddress, BaseModel
from sqlalchemy import JSON, SmallInteger, Column, CHAR, UUID
from typing import Optional
import datetime
import uuid

class Response(BaseModel):
    detail:         str = '' 
    status_code:    int = 200
    data:           dict | list | None = None

class SQLModel(_SQLModel):
    created_at:     datetime.datetime = Field(default_factory=datetime.datetime.now)
    # 不能用 uuid 定义
    id:             str = Field(default_factory=uuid.uuid4, primary_key=True)
    available:      int = Field(sa_type=SmallInteger, default=1)

class User(SQLModel, table=True):
    name:           str
    password:       bytes
    email:          str | None = Field(default=None)
    phone_number:   str | None = Field(default=None)
    ip:             str | None = Field(default=None)
    addition:       dict = Field(sa_type=JSON, default={})

    files:          list["File"] = Relationship(back_populates="publisher")

class File(SQLModel, table=True):
    file_type:      str = Field(default=None)
    file_md5:       str = Field(sa_column=Column(CHAR(32)))
    file_name:      str = Field(default=None)
    file_path:      str = Field(default=None)
    size:           int = Field(default=-1)

    publisher_id:   str = Field(default=None, foreign_key="user.id")
    publisher:      User | None = Relationship(back_populates="files")