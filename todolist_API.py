from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, ClassVar
from uuid import uuid4


app = FastAPI()

class TodoItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: str
    allowed_priorities: ClassVar[List[str]] = ["Low", "Medium", "High"]

todo_list: List[TodoItem] = []

@app.post("/todos/", response_model=TodoItem)
def create_todo_item(item: TodoItem):
    if item.priority not in TodoItem.allowed_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority level")
    item.id = str(uuid4())
    todo_list.append(item)
    return item
    
@app.get("/todos/", response_model=List[TodoItem])
def get_todo_items():
    return todo_list

@app.get("/todos/{item_id}", response_model=TodoItem)
def get_todo_item(item_id: str):
    for item in todo_list:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/todos/{item_id}", response_model=TodoItem)
def update_todo_item(item_id: str, updated_item: TodoItem):
    for index, item in enumerate(todo_list):
        if item.id == item_id:
            if updated_item.priority not in TodoItem.allowed_priorities:
                raise HTTPException(status_code=400, detail="Invalid priority level")
            item_id = updated_item.id
            updated_item = todo_list[index]
            return updated_item
        raise HTTPException(status_code=404, detail="Item not found")
    
@app.delete("/todos/{item_id}")
def delete_todo_item(item_id: str):
    for index, item in enumerate(todo_list):
        if item.id == item_id:
            del todo_list[index]
            return {"detail": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/todos/priority/{priority_level}", response_model=List[TodoItem])
def get_todo_items_by_priority(priority_level: str):
    if priority_level not in TodoItem.allowed_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority level")
    filtered_items = [item for item in todo_list if item.priority == priority_level]
    return filtered_items

@app.delete("/todos/")
def delete_all_todo_items():
    global todo_list
    todo_list.clear()
    return {"detail": "All items deleted"}

@app.get("/todos/count/", response_model=int)
def count_todo_items():
    return len(todo_list)

@app.get("/todos/count/priority/{priority_level}", response_model=int)
def count_todo_items_by_priority(priority_level: str):
    if priority_level not in TodoItem.allowed_priorities:
        raise HTTPException(status_code=400, detail="Invalid priority level")
    count = sum(1 for item in todo_list if item.priority == priority_level)
    return count

@app.get("/todos/search/", response_model=List[TodoItem])
def search_todo_items(query: str):
    result = [item for item in todo_list if query.lower() in item.title.lower() or (item.description and query.lower() in item.description.lower())]
    return result

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo List API"}

@app.get("/health/")
def health_check():
    return {"status": "OK"}

@app.get("/todos/stats/")
def get_todo_stats():
    stats = {priority: 0 for priority in TodoItem.allowed_priorities}
    for item in todo_list:
        stats[item.priority] += 1
    return stats

@app.get("/todos/duplicates/", response_model=List[TodoItem])
def get_duplicate_todo_items():
    seen = set()
    duplicates = []
    for item in todo_list:
        identifier = (item.title, item.description, item.priority)
        if identifier in seen:
            duplicates.append(item)
        else:
            seen.add(identifier)
    return duplicates

@app.post("/todos/duplicate_check/", response_model=bool)
def check_duplicate_todo_item(item: TodoItem):
    identifier = (item.title, item.description, item.priority)
    for existing_item in todo_list:
        if (existing_item.title, existing_item.description, existing_item.priority) == identifier:
            return True
    return False

@app.get("/todos/export/", response_model=List[TodoItem])
def export_todo_items():
    return todo_list

@app.post("/todos/import/", response_model=List[TodoItem])
def import_todo_items(items: List[TodoItem]):
    imported_items = []
    for item in items:
        if item.priority not in TodoItem.allowed_priorities:
            raise HTTPException(status_code=400, detail=f"Invalid priority level for item: {item.title}")
        item.id = str(uuid4())
        todo_list.append(item)
        imported_items.append(item)
    return imported_items
