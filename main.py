from fastapi import FastAPI, HTTPException, Depends, Body, Path
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
from typing import Annotated
from sqlalchemy.orm import Session
import uuid

from db import get_db, LinksDB, Base, engine

app = FastAPI(title="URL Shortener API")
Base.metadata.create_all(bind=engine)

@app.get('/', tags=["System"])
async def root():
    """
    **Главная**
    Возвращает информацию о проекте и доступных эндпоинтах.
    """
    return {
        "Project": "URL Shortener API",
        "Status": "Running",
        "Documentation": "/docs",
        "Message": "Welcome! Go to /docs for interactive testing."
    }

@app.post('/shorten', tags=["User Endpoints"])
async def shorten(link: HttpUrl, db: Session = Depends(get_db)):
    """
    **Создать короткую ссылку.**
    
    - Генерирует уникальный 4-символьный код.
    - Проверяет базу на наличие дубликатов кода.
    """
    while True:
        short_link = str(uuid.uuid4())[:4]
        query = db.query(LinksDB).filter(LinksDB.short_link == short_link).first()
        if not query:
            break
            
    new_obj = LinksDB(short_link=short_link, long_link=str(link))
    db.add(new_obj)
    db.commit()
    return {'status': 'success', 'short_code': short_link}

@app.get('/links', tags=["Admin Endpoints"])
async def get_all_links(db: Session = Depends(get_db)):
    """
    **Получить все ссылки.**
    
    Выводит список ссылок, хранящихся в базе данных.
    """
    all_links = db.query(LinksDB).all()
    if not all_links:
        raise HTTPException(status_code=404, detail='База данных пуста')
    
    return [
        {"id": link.id, "short_link": link.short_link, "long_link": link.long_link} 
        for link in all_links
    ]

@app.get('/links/{short_link}', tags=["Admin Endpoints"])
async def search_link(
    short_link: str = Path(..., description="Код ссылки для поиска"), 
    db: Session = Depends(get_db)
):
    """
    **Поиск ссылки по коду.**
    
    Выводит конкретную пару ссылок
    """
    found_link = db.query(LinksDB).filter(LinksDB.short_link == short_link).first()
    if found_link:
        return {"short_link": short_link, "long_link": found_link.long_link}
    raise HTTPException(status_code=404, detail='Ссылка не найдена')

@app.get('/{link}', tags=["User Endpoints"])
async def redirect_to_url(link: str, db: Session = Depends(get_db)):
    """
    **Редирект.**
    
    Принимает короткую ссылку и перенаправляет пользователя на оригинальный URL.
    """
    db_item = db.query(LinksDB).filter(LinksDB.short_link == link).first()
    if db_item:
        return RedirectResponse(url=db_item.long_link)
    raise HTTPException(status_code=404, detail='Ссылка не найдена')

@app.delete('/links/{short_link}', tags=["Admin Endpoints"])
async def delete_link(short_link: str, db: Session = Depends(get_db)):
    """
    **Удаление ссылки.**
    
    Навсегда удаляет запись о ссылке из базы данных.
    """
    del_link = db.query(LinksDB).filter(LinksDB.short_link == short_link).first()
    if del_link:
        db.delete(del_link)
        db.commit()
        return {'status': 'deleted', 'short_code': short_link}
    raise HTTPException(status_code=404, detail='Ссылка не найдена')

@app.patch('/links/{short_link}', tags=["Admin Endpoints"])
async def update_link(
    short_link: str, 
    new_link: Annotated[str, Body(embed=True)], 
    db: Session = Depends(get_db)
):
    """
    **Обновление ссылки.**
    
    Позволяет изменить URL для уже существующей короткой ссылки.
    """
    found_link = db.query(LinksDB).filter(LinksDB.short_link == short_link).first()
    if found_link:
        found_link.long_link = str(new_link)
        db.commit()
        return {'status': 'updated', 'short_code': short_link}
    raise HTTPException(status_code=404, detail='Ссылка не найдена')