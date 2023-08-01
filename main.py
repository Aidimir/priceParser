import requests
from bs4 import BeautifulSoup as bs
from db import add_to_db, remove_by_id, fetch_from_db, Price
from fastapi import FastAPI, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import threading
from typing import List

PRODUCT_URL = "https://www.1sm.ru/catalog/komplektuyushchie/videokarty/"

description = """
Price-parser API made to parse info about products. 🚀
"""

tags_metadata = [
    {
        "name": "fetch",
        "description": "fetches products info (title, price, id)",
    },
]



app = FastAPI(title="ParserService",
              description=description,
              version="0.0.1",
              openapi_tags=tags_metadata,
              # docs_url=None,
              redoc_url=None,
              )


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:4200",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def update_storage():
    threading.Timer(interval=3600.0, function=update_storage).start()
    update_db()


@app.get("/fetch", tags=["fetch"])
async def fetch():
    items = fetch_from_db()
    return items


async def update_db():
    try:
        # requests solution
        page = requests.get(url=PRODUCT_URL)
        html = page.text

        soup = bs(html, "lxml")
        items = soup.find_all("div", class_="item_info main_item_wrapper TYPE_1")
        products = []
        for item in items:
            title = item.find("div", class_="item-title").text
            title = title.replace("\n", "")
            price = item.find("div", class_="cost prices clearfix").find("div", class_="price")
            id = item.find_all("div", class_="item-stock")[1].find("span", class_="value")
            id = int(id.text)
            price = price.text.replace(" ", "")[:-4]
            price = int(price.replace("\n", ""))
            form = Price(id=id, name=title, price=price)
            add_to_db(form)
            json_form = {"id": id, "title": title, "price": price}
            products.append(json_form)
            print(title)
            print("price: ", price)
            print("code: ", id)
        return products
    except:
        raise HTTPException(status_code=400, detail="Couldn't fetch any data")

@app.post("/add")
async def add(title: str, price: int, code: int):
    try:
        form = Price(id=code, name=title, price=price)
        add_to_db(form)
    except:
        raise HTTPException(status_code=400, detail="Couldn't fetch any data")

@app.delete("/delete")
async def delete(id: int):
    try:
        remove_by_id(id)
        return fetch_from_db()
    except:
        raise HTTPException(status_code=400, detail="Couldn't fetch any data")


@app.put("/update")
async def update(title: str, price: int, code: int):
    try:
        form = Price(id=code, name=title, price=price)
        add_to_db(form)
    except:
        raise HTTPException(status_code=400, detail="Couldn't fetch any data")

update_storage()