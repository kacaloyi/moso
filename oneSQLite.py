
#如何以灵活的方式为sqlalchemy使用嵌套的pydantic模型
#https://www.zhblog.net/qa/a-flexible-way.html

from fastapi import Depends, FastAPI, HTTPException, Body, Request
from sqlalchemy import create_engine, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, relationship
from sqlalchemy.inspection import inspect
from typing import List, Optional
from pydantic import BaseModel
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
app = FastAPI()


# sqlalchemy models

class RootModel(Base):
    __tablename__ = "root_table"
    id = Column(Integer, primary_key=True, index=True)
    someRootText = Column(String)
    subData = relationship("SubModel", back_populates="rootData")


class SubModel(Base):
    __tablename__ = "sub_table"
    id = Column(Integer, primary_key=True, index=True)
    someSubText = Column(String)
    root_id = Column(Integer, ForeignKey("root_table.id"))
    rootData = relationship("RootModel", back_populates="subData")


# pydantic models/schemas
class SchemaSubBase(BaseModel):
    someSubText: str

    class Config:
        orm_mode = True


class SchemaSub(SchemaSubBase):
    id: int
    root_id: int

    class Config:
        orm_mode = True


class SchemaRootBase(BaseModel):
    someRootText: str
    subData: List[SchemaSubBase] = []

    class Config:
        orm_mode = True


class SchemaRoot(SchemaRootBase):
    id: int

    class Config:
        orm_mode = True


class SchemaSimpleBase(BaseModel):
    someRootText: str

    class Config:
        orm_mode = True


class SchemaSimple(SchemaSimpleBase):
    id: int

    class Config:
        orm_mode = True


Base.metadata.create_all(bind=engine)


# database functions (CRUD)

def db_add_simple_data_pydantic(db: Session, root: SchemaRootBase):
    db_root = RootModel(**root.dict())
    db.add(db_root)
    db.commit()
    db.refresh(db_root)
    return db_root


def db_add_nested_data_pydantic_generic(db: Session, root: SchemaRootBase):

    # this fails:
    db_root = RootModel(**root.dict())
    db.add(db_root)
    db.commit()
    db.refresh(db_root)
    return db_root


def db_add_nested_data_pydantic(db: Session, root: SchemaRootBase):

    # start: hack: i have to manually generate the sqlalchemy model from the pydantic model
    root_dict = root.dict()
    sub_dicts = []

    # i have to remove the list form root dict in order to fix the error from above
    for key in list(root_dict):
        if isinstance(root_dict[key], list):
            sub_dicts = root_dict[key]
            del root_dict[key]

    # now i can do it
    db_root = RootModel(**root_dict)
    for sub_dict in sub_dicts:
        db_root.subData.append(SubModel(**sub_dict))

    # end: hack
    db.add(db_root)
    db.commit()
    db.refresh(db_root)
    return db_root


def db_add_nested_data_nopydantic(db: Session, root):
    print(root)
    sub_dicts = root.pop("subData")
    print(sub_dicts)
    db_root = RootModel(**root)

    for sub_dict in sub_dicts:
        db_root.subData.append(SubModel(**sub_dict))
    db.add(db_root)
    db.commit()
    db.refresh(db_root)

    # problem
    """
    if I would now "return db_root", the answer would be of this:
    {
        "someRootText": "string",
        "id": 24
    }

    and not containing "subData"
    therefore I have to do the following.
    Why?

    """
    from sqlalchemy.orm import joinedload

    db_root = (
        db.query(RootModel)
            .options(joinedload(RootModel.subData))
            .filter(RootModel.id == db_root.id)
            .all()
    )[0]
    return db_root


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/addNestedModel_pydantic_generic", response_model=SchemaRootBase)
def addSipleModel_pydantic_generic(root: SchemaRootBase, db: Session = Depends(get_db)):
    data = db_add_simple_data_pydantic(db=db, root=root)
    return data


@app.post("/addSimpleModel_pydantic", response_model=SchemaSimpleBase)
def add_simple_data_pydantic(root: SchemaSimpleBase, db: Session = Depends(get_db)):
    data = db_add_simple_data_pydantic(db=db, root=root)
    return data


@app.post("/addNestedModel_nopydantic")
def add_nested_data_nopydantic(root=Body(...), db: Session = Depends(get_db)):
    data = db_add_nested_data_nopydantic(db=db, root=root)
    return data


@app.post("/addNestedModel_pydantic", response_model=SchemaRootBase)
def add_nested_data_pydantic(root: SchemaRootBase, db: Session = Depends(get_db)):
    data = db_add_nested_data_pydantic(db=db, root=root)
    return data