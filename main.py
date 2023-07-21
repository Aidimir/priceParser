import requests
from bs4 import BeautifulSoup as bs
from db import add_to_db, Price
from fastapi import FastAPI, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import json
from sqlalchemy.ext.declarative import DeclarativeMeta
from uuid import UUID

class OutputMixin(object):
    RELATIONSHIPS_TO_DICT = False

    def __iter__(self):
        return self.to_dict().iteritems()

    def to_dict(self, rel=None, backref=None):
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        res = {column.key: getattr(self, attr)
               for attr, column in self.__mapper__.c.items()}
        if rel:
            for attr, relation in self.__mapper__.relationships.items():
                # Avoid recursive loop between to tables.
                if backref == relation.table:
                    continue
                value = getattr(self, attr)
                if value is None:
                    res[relation.key] = None
                elif isinstance(value.__class__, DeclarativeMeta):
                    res[relation.key] = value.to_dict(backref=self.__table__)
                else:
                    res[relation.key] = [i.to_dict(backref=self.__table__)
                                         for i in value]
        return res

    def to_json(self, rel=None):
        def extended_encoder(x):
            if isinstance(x, UUID):
                return str(x)
        if rel is None:
            rel = self.RELATIONSHIPS_TO_DICT
        return json.dumps(self.to_dict(rel), default=extended_encoder)


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

@app.post("/fetch", tags=["fetch"])
async def fetch():
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