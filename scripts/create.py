import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # db.execute("DROP TABLE books CASCADE;")
    # db.execute("DROP TABLE users CASCADE;")
    # db.execute("DROP TABLE reviews CASCADE;")

    db.execute("CREATE TABLE books(      \
                    id SERIAL PRIMARY KEY,\
                    isbn VARCHAR NOT NULL, \
                    title VARCHAR NOT NULL, \
                    author VARCHAR NOT NULL, \
                    year VARCHAR NOT NULL,    \
                    review_count INTEGER,      \
                    averege_score DECIMAL       \
                );")
    
    db.execute("CREATE TABLE users(         \
                    id SERIAL PRIMARY KEY,   \
                    username VARCHAR NOT NULL,\
                    password VARCHAR NOT NULL  \
                );")

    db.execute("CREATE TABLE reviews(               \
                    id SERIAL PRIMARY KEY,           \
                    user_id INTEGER REFERENCES users, \
                    book_id INTEGER REFERENCES books, \
                    rating_score DECIMAL NOT NULL,     \
                    review VARCHAR NOT NULL             \
                );")
    db.commit()

    print(f"Created Tables")

if __name__ == "__main__":
    main()