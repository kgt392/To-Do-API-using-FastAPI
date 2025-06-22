from fastapi import FastAPI, Depends, HTTPException,Path
from sqlalchemy.orm import Session

import models
from database import engine, SessionLocal
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class  TodoCreate(BaseModel):
    title :str
    description : Optional[str] =None
    priority :int
    due_date :datetime
    completed :bool


@app.get("/todos")
def get_all_todo(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

@app.get("/todo/{todo_id}")
def get_single_todo(todo_id:int = Path(...,description = "Enter id to view Task .."),db: Session = Depends(get_db),):
    todo= db.query(models.Todo).filter(models.Todo.id==todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    return todo

@app.post("/todo/")
def create_a_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todo/{todo_id}")
def delete_a_todo(todo_id:int = Path(...,description = "Enter id to delete Task .."),db: Session = Depends(get_db)):
    todo= db.query(models.Todo).filter(models.Todo.id==todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(todo)
    db.commit()
    return {"message":"deleted the task"}

@app.put("/todo/{todo_id}")
def update_a_todo(*,todo_id:int = Path(...,description = "Enter id to update Task .."),Update_todo:TodoCreate,db: Session = Depends(get_db)):
    todo= db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")
    todo.title =Update_todo.title
    todo.description =Update_todo.description
    todo.priority =Update_todo.priority
    todo.due_date =Update_todo.due_date
    todo.completed =Update_todo.completed
    db.commit()
    db.refresh(todo)
    return {"data":todo}
