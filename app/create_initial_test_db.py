from sqlmodel import SQLModel, create_engine, Session

from app.model import User, Todo
import os

# sql_url = f"sqlite:///app/database.db"
sql_url = os.getenv("DB_URL")

engine = create_engine(sql_url, echo=True)


def create_tables():
    SQLModel.metadata.create_all(engine)


def create_user():
    user1 = User(name="Davud", password="admin", disabled=False)
    with Session(engine) as session:
        session.add(user1)
        session.commit()


def create_todos():
    todo1 = Todo(name="Push ups", description="Do many many push ups repeatedly.", owner_id=1)
    todo2 = Todo(name="Pull ups", description="Do not so many pull ups repeatedly.", owner_id=1)

    with Session(engine) as session:
        session.add(todo1)
        session.add(todo2)
        session.commit()


def main():
    create_tables()
    create_user()
    create_todos()


if __name__ == '__main__':
    main()
