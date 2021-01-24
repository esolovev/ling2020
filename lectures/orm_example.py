from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:')
Base = declarative_base()


# описали с помощью класса таблицу users
class User(Base):
    __tablename__ = 'users'

    # метакласс превратит всю эту шляпу в нормальные атрибуты
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
            self.name, self.fullname, self.nickname)


Base.metadata.create_all(engine)


ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')  # создали объект юзера

print('Type of class User: ', type(User))  # так мы понимаем, что при создании User задействован метакласс

print('ID', ed_user.id)  # нормальные атрибуты
print('NAME', ed_user.name)

Session = sessionmaker(bind=engine)
session = Session()
session.add(ed_user)  # добавили запись про юзера в бд в таблицу users
our_user = session.query(User).filter_by(name='ed').first()

print('User form table users', our_user)
