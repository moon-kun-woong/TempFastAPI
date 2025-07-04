import sqlite3
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from . import schemas


def row_to_dict(row) -> Dict[str, Any]:
    """SQLite Row 객체를 딕셔너리로 변환"""
    if not row:
        return {}
    
    return {key: str(value) if key == 'created_at' else value for key, value in dict(row).items()}


def get_item_by_title(db: sqlite3.Connection, title: str) -> Optional[Dict[str, Any]]:
    """제목으로 아이템 조회"""
    query = "SELECT * FROM items WHERE title = ?"
    cursor = db.execute(query, (title,))
    item = cursor.fetchone()
    return row_to_dict(item) if item else None


def create_item(db: sqlite3.Connection, item: schemas.ItemCreate) -> Dict[str, Any]:
    """새 아이템 생성"""
    existing_item = get_item_by_title(db, title=item.title)
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item with title '{item.title}' already exists"
        )
        
    item_data = item.model_dump()
    
    query = """INSERT INTO items (title, description, is_active) 
              VALUES (?, ?, ?)"""
    cursor = db.execute(
        query, 
        (item_data['title'], item_data.get('description'), item_data.get('is_active', True))
    )
    
    created_id = cursor.lastrowid
    return get_item(db, created_id)


def get_items(db: sqlite3.Connection, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    """아이템 목록 조회"""
    query = "SELECT * FROM items LIMIT ? OFFSET ?"
    cursor = db.execute(query, (limit, skip))
    items = cursor.fetchall()
    return [row_to_dict(item) for item in items]


def get_item(db: sqlite3.Connection, item_id: int) -> Dict[str, Any]:
    """ID로 아이템 조회"""
    query = "SELECT * FROM items WHERE id = ?"
    cursor = db.execute(query, (item_id,))
    item = cursor.fetchone()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return row_to_dict(item)


def update_item(db: sqlite3.Connection, item_id: int, item: schemas.ItemUpdate) -> Dict[str, Any]:
    """아이템 수정"""
    existing_item = get_item(db, item_id)
    update_data = item.model_dump(exclude_unset=True)
    if not update_data:
        return existing_item
    
    if 'title' in update_data:
        title_check = get_item_by_title(db, title=update_data['title'])
        if title_check and title_check['id'] != item_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with title '{update_data['title']}' already exists"
            )
    
    update_fields = []
    params = []
    
    for key, value in update_data.items():
        if key in ['title', 'description', 'is_active']:
            update_fields.append(f"{key} = ?")
            params.append(value)
    
    if not update_fields:
        return existing_item
    
    query = f"UPDATE items SET {', '.join(update_fields)} WHERE id = ?"
    params.append(item_id)
    db.execute(query, params)
    
    return get_item(db, item_id)


def delete_item(db: sqlite3.Connection, item_id: int) -> Dict[str, Any]:
    """아이템 삭제"""
    item = get_item(db, item_id)
    
    query = "DELETE FROM items WHERE id = ?"
    db.execute(query, (item_id,))
    
    return item
