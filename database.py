from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import String,Integer,Float,DateTime

class Base(DeclarativeBase):
    pass
class User((Base)):
    __tablename__='users'
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100),unique=True)
    hashed_pw: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[DateTime] = mapped_column(DateTime)

class Budget(Base):
    __tablename__="mybudget"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    amount: Mapped[float] = mapped_column(Float)
    date: Mapped[DateTime] = mapped_column(DateTime)