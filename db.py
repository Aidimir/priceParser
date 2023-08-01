from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()
class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)

DB_NAME = "sqlite:///prices.sqlite"
engine = create_engine(DB_NAME)
session = Session(bind=engine)

with engine.connect() as conn:
    if not conn.dialect.has_table(conn, "price"):  # If table don't exist, Create.
        Base.metadata.create_all(bind=engine)
        print("CREATED")
    else:
        print("ALREADY EXISTS")

def remove_from_db(item):
    session.delete(item)
    session.commit()

def remove_by_id(id):
    obj = session.query(Price).filter_by(id=id).scalar()
    if obj is not None:
        remove_from_db(obj)

def add_to_db(item):
    remove_by_id(item.id)
    session.add(item)
    session.commit()

def fetch_from_db() -> [Price]:
    return session.query(Price).all()