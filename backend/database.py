import os
from datetime import date

from sqlalchemy import Column, Date, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

DB_PATH = os.getenv("DB_PATH", "ib_viewer.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class CapitalInjectionRow(Base):
    __tablename__ = "capital_injections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount_cny = Column(Float, nullable=False)
    injected_on = Column(Date, nullable=False)
    note = Column(String, default="")


def init_db():
    Base.metadata.create_all(engine)


# CRUD helpers

def get_all_injections() -> list[CapitalInjectionRow]:
    with Session(engine) as s:
        return s.query(CapitalInjectionRow).order_by(CapitalInjectionRow.injected_on).all()


def add_injection(amount_cny: float, injected_on: date, note: str) -> CapitalInjectionRow:
    with Session(engine) as s:
        row = CapitalInjectionRow(amount_cny=amount_cny, injected_on=injected_on, note=note)
        s.add(row)
        s.commit()
        s.refresh(row)
        return row


def delete_injection(injection_id: int) -> bool:
    with Session(engine) as s:
        row = s.get(CapitalInjectionRow, injection_id)
        if row is None:
            return False
        s.delete(row)
        s.commit()
        return True
