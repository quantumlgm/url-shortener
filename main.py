from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
from typing import Annotated
import uuid

app = FastAPI()
links_db = {}

@app.post('/shorten')
async def shorten(link: HttpUrl) -> dict:
    while True:
        short_link = str(uuid.uuid4())[:4]
        if short_link in links_db:
            continue
        else:
            break
    links_db[short_link] = str(link.link)
    return {'Status': '200', 'Description': 'OK'}

@app.get('/links')
async def links() -> dict:
    if links_db:
        return links_db
    raise HTTPException(status_code=404, detail='База данных пуста. Добавьте ссылку')

@app.get('/links/{link}')
async def search_link(link: str) -> dict:
    if link in links_db:
        return {link: links_db[link]}
    raise HTTPException(status_code=404, detail='Ссылки не обнаружено')

@app.get('/{link}')
async def new_link(link: str):
    if link in links_db:
        return RedirectResponse(links_db[link])
    raise HTTPException(status_code=404, detail='Ссылки не обнаружено')

@app.delete('/links/{link}')
async def delete_link(link: str) -> dict:
    if link in links_db:
        del links_db[link]
        return {'Status': '200', 'Description': 'Успешно удалено'}
    raise HTTPException(status_code=404, detail='Ссылки не обнаружено')

@app.patch('/links/{link}')
async def patch_link(link: str, new_link: Annotated[str, Body()]) -> dict:
    if link in links_db:
        links_db[link] = new_link
        return {'Status': '200', 'Description': 'Успешно изменено'}
    raise HTTPException(status_code=404, detail='Ссылки не обнаружено')