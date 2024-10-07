from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base, async_engine
import enum


# 사용자 엔티티
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    reservations = relationship("Reservation", back_populates="user")


# 콘서트 엔티티
class Concert(Base):
    __tablename__ = "concert"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    event_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # 콘서트에 대한 좌석들
    seats = relationship("Seat", back_populates="concert")
    tickets = relationship("Ticket", back_populates="concert")


# 좌석 엔티티
class Seat(Base):
    __tablename__ = "seat"

    id = Column(Integer, primary_key=True, index=True)
    concert_id = Column(Integer, ForeignKey("concert.id"), nullable=False)
    seat_number = Column(String(10), nullable=False)
    section = Column(String(10))

    concert = relationship("Concert", back_populates="seats")
    ticket = relationship("Ticket", back_populates="seat")


# 티켓 엔티티
class TicketStatus(enum.Enum):
    available = "available"
    reserved = "reserved"
    sold = "sold"


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True, index=True)
    concert_id = Column(Integer, ForeignKey("concert.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seat.id"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.available)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # 티켓과 좌석, 콘서트 관계
    concert = relationship("Concert", back_populates="tickets")
    seat = relationship("Seat", back_populates="ticket", uselist=False)
    reservation = relationship("Reservation", back_populates="ticket", uselist=False)


# 예약 엔티티
class ReservationStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    canceled = "canceled"


class Reservation(Base):
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("ticket.id"), nullable=False)
    reserved_at = Column(DateTime(timezone=True), default=func.now())
    status = Column(Enum(ReservationStatus), default=ReservationStatus.pending)

    # 예약과 사용자, 티켓 관계
    user = relationship("User", back_populates="reservations")
    ticket = relationship("Ticket", back_populates="reservation")


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
