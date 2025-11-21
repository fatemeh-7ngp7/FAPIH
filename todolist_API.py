from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, ClassVar
from uuid import uuid4
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "mysql+pymysql://fati:your_password@localhost:3306/todo_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TodoItemDB(Base):
    __tablename__ = "todos"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    priority = Column(String(50), nullable=False)

app = FastAPI()

class TodoItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: str
    allowed_priorities: ClassVar[List[str]] = ["Low", "Medium", "High"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. For production, specify exact origins: ["http://localhost:8080", "http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


#todo_list: List[TodoItem] = []

@app.post("/todos/", response_model=TodoItem)
def create_todo_item(item: TodoItem, db: Session = Depends(get_db)):
    if item.priority not in TodoItem.allowed_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority level")
    db_item = TodoItemDB(
        id=str(uuid4()),
        title=item.title,
        description=item.description,
        priority=item.priority
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
    
@app.get("/todos/", response_model=List[TodoItem])
def get_todo_items(db: Session = Depends(get_db)):
    return db.query(TodoItemDB).all()

@app.get("/todos/{item_id}", response_model=TodoItem)
def get_todo_item(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(TodoItemDB).filter(TodoItemDB.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/todos/{item_id}", response_model=TodoItem)
def update_todo_item(item_id: str, updated_item: TodoItem, db: Session = Depends(get_db)):
    db_item = db.query(TodoItemDB).filter(TodoItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if updated_item.priority not in TodoItem.allowed_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority level")
    db_item.title = updated_item.title                       # type: ignore
    db_item.description = updated_item.description              # type: ignore
    db_item.priority = updated_item.priority                  # type: ignore
    db.commit()
    db.refresh(db_item)
    return db_item

    
@app.delete("/todos/{item_id}")
def delete_todo_item(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(TodoItemDB).filter(TodoItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Item deleted"}

@app.get("/todos/priority/{priority_level}", response_model=List[TodoItem])
def get_todo_items_by_priority(priority_level: str, db: Session = Depends(get_db)):
    if priority_level not in TodoItem.allowed_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority level")
    filtered_items = db.query(TodoItemDB).filter(TodoItemDB.priority == priority_level).all()
    return filtered_items

@app.delete("/todos/")
def delete_all_todo_items(db: Session = Depends(get_db)):
    db.query(TodoItemDB).delete()
    db.commit()
    return {"detail": "All items deleted"}

@app.get("/todos/count/", response_model=int)
def count_todo_items(db: Session = Depends(get_db)):
    return db.query(TodoItemDB).count()


@app.get("/todos/count/priority/{priority_level}", response_model=int)
def count_todo_items_by_priority(priority_level: str, db: Session = Depends(get_db)):
    if priority_level not in TodoItem.allowed_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority level")
    count = db.query(TodoItemDB).filter(TodoItemDB.priority == priority_level).count()
    return count

@app.get("/todos/search/", response_model=List[TodoItem])
def search_todo_items(query: str, db: Session = Depends(get_db)):
    result = db.query(TodoItemDB).filter(
        (TodoItemDB.title.ilike(f"%{query}%")) | 
        (TodoItemDB.description.ilike(f"%{query}%"))
    ).all()
    return result

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo List API"}

@app.get("/health/")
def health_check():
    return {"status": "OK"}

from sqlalchemy import func

@app.get("/todos/stats/")
def get_todo_stats(db: Session = Depends(get_db)):
    stats = {priority: 0 for priority in TodoItem.allowed_priorities}
    results = db.query(TodoItemDB.priority, func.count(TodoItemDB.id)).group_by(TodoItemDB.priority).all()
    for priority, count in results:
        stats[priority] = count
    return stats


@app.get("/todos/duplicates/", response_model=List[TodoItem])
def get_duplicate_todo_items(db: Session = Depends(get_db)):
    seen = set()
    duplicates = []
    for item in db.query(TodoItemDB).all():
        identifier = (item.title, item.description, item.priority)
        if identifier in seen:
            duplicates.append(item)
        else:
            seen.add(identifier)
    return duplicates

@app.post("/todos/duplicate_check/", response_model=bool)
def check_duplicate_todo_item(item: TodoItem, db: Session = Depends(get_db)):
    identifier = (item.title, item.description, item.priority)
    for existing_item in db.query(TodoItemDB).all():
        if (existing_item.title, existing_item.description, existing_item.priority) == identifier:
            return True
    return False

@app.get("/todos/export/", response_model=List[TodoItem])
def export_todo_items(db: Session = Depends(get_db)):
    return db.query(TodoItemDB).all()

@app.post("/todos/import/", response_model=List[TodoItem])
def import_todo_items(items: List[TodoItem], db: Session = Depends(get_db)):
    imported_items = []
    for item in items:
        if item.priority not in TodoItem.allowed_priorities:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid priority level for item: {item.title}"
            )
        db_item = TodoItemDB(
            id=str(uuid4()),
            title=item.title,
            description=item.description,
            priority=item.priority
        )
        db.add(db_item)
        imported_items.append(db_item)
    db.commit()
    # تازه‌سازی داده‌ها بعد از ذخیره
    for db_item in imported_items:
        db.refresh(db_item)
    return imported_items

