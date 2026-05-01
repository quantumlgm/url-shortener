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
    return {
        "Project": "URL Shortener API",
        "Status": "Running",
        "Documentation": "/docs",
        "Message": "Welcome! Go to /docs for interactive testing."
    }

@app.post('/shorten', tags=["User Endpoints"])
async def shorten(link: HttpUrl, db: Session = Depends(get_db)):
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
    found_link = db.query(LinksDB).filter(LinksDB.short_link == short_link).first()
    if found_link:
        return {"short_link": short_link, "long_link": found_link.long_link}
    raise HTTPException(status_code=404, detail='Ссылка не найдена')

@app.get('/{link}', tags=["User Endpoints"])
async def redirect_to_url(link: str, db: Session = Depends(get_db)):
    db_item = db.query(LinksDB).filter(LinksDB.short_link == link).first()
    if db_item:
        return RedirectResponse(url=db_item.long_link)
    raise HTTPException(status_code=404, detail='Ссылка не найдена')

@app.delete('/links/{short_link}', tags=["Admin Endpoints"])
async def delete_link(short_link: str, db: Session = Depends(get_db)):
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
    found_link = db.query(LinksDB).filter(LinksDB.short_link == short_link).first()
    if found_link:
        found_link.long_link = str(new_link)
        db.commit()
        return {'status': 'updated', 'short_code': short_link}
    raise HTTPException(status_code=404, detail='Ссылка не найдена')
