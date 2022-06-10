from sqlmodel import SQLModel, create_engine, Session

from model import User, Todo
import os




# sqlite_file_name = "app/database.db"
# sql_url = f"sqlite:///{sqlite_file_name}"
sql_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:5432/{os.getenv('POSTGRES_DB')}"


engine = create_engine(sql_url, echo=True)

def create_tables():
    SQLModel.metadata.create_all(engine)


def create_user():
    user1 = User(name="Davud")
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
