
from unittest import TestCase

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode


Base = declarative_base()


class Grandparent(Base):

    __tablename__ = 'grandparents'
    id = Column(Integer, primary_key=True)


class Parent(Base):

    __tablename__ = 'parents'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    parent_id = Column(Integer, ForeignKey(Grandparent.id), nullable=False)
    parent = relationship(Grandparent, backref='children')


class Child(Base):

    __tablename__ = 'children'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(Parent.id), nullable=False)
    parent = relationship(Parent, backref='children')


class SessionTest(TestCase):

    def test_error(self):
        try:
            engine = create_engine('sqlite:///')
            metadata = Base.metadata
            metadata.bind=engine
            metadata.create_all()
            Session = sessionmaker(bind=engine)
            session = Session()
            parent1 = Parent(name='parent1')
            child1 = Child(parent=parent1)
            session.add(child1)
            parent2 = session.query(Parent).filter(Parent.name=='parent1').one()
            child2 = Child(parent=parent2)
            assert False, 'expected error'
        except:
            pass
