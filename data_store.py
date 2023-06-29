from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData, Column, Integer
from sqlalchemy.orm import Session
from config import db_url_object


Base = declarative_base()
metadata = MetaData()
engine = create_engine(db_url_object)


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)

    def add_user(engine, profile_id, user_id):
        with Session(engine) as session:
            to_bd = Viewed(profile_id=profile_id, user_id=user_id)
        session.add(to_bd)
        session.commit()

    def check_user(engine, profile_id, user_id):
        with Session(engine) as session:
            from_bd = session.query(Viewed).filter(
            Viewed.profile_id == profile_id,
            Viewed.user_id == user_id
        ).first()
        return True if from_bd else False


if __name__ == '__main__':
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    Viewed.add_user(engine, 2113, 654623)
    res = Viewed.check_user(engine, 195050304, 294362311)
    print(res)