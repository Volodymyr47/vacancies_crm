from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os


DB_LOCAL = 'postgresql://postgres:mysecretpassword@localhost:5432/vacanciesdb'
DB_URL = os.environ.get("DATABASE_URL", DB_LOCAL)


engine = create_engine(DB_URL, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as err:
        print(err)
        return False
