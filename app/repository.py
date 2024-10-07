from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.model import User, Concert, Seat, Ticket, TicketStatus, Reservation, ReservationStatus


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int):
        result = await self.session.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def create_user(self, username: str, email: str):
        user = User(username=username, email=email)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user


class ConcertRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_concert_by_id(self, concert_id: int):
        result = await self.session.execute(select(Concert).filter(Concert.id == concert_id))
        return result.scalars().first()

    async def get_seats_by_concert_id(self, concert_id: int):
        result = await self.session.execute(select(Seat).where(Seat.concert_id == concert_id))
        return result.scalars().all()

    async def create_concert(self, name: str, event_date):
        concert = Concert(name=name, event_date=event_date)
        self.session.add(concert)
        await self.session.flush()
        await self.session.refresh(concert)
        return concert

    async def create_seats(self, concert_id: int, total_seats: int):
        concert = await self.get_concert_by_id(concert_id)
        if not concert:
            return None

        for i in range(1, total_seats + 1):
            seat = Seat(concert_id=concert_id, seat_number=str(i), section="A")
            self.session.add(seat)
        await self.session.flush()
        await self.session.refresh(concert)
        return f"{total_seats} seats created for concert {concert_id}"


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_ticket_by_id(self, ticket_id: int):
        result = await self.session.execute(select(Ticket).filter(Ticket.id == ticket_id))
        return result.scalars().first()

    async def create_ticket(self, concert_id: int, seat_id: int, price: float):
        ticket = Ticket(concert_id=concert_id, seat_id=seat_id, price=price, status=TicketStatus.available)
        self.session.add(ticket)
        await self.session.flush()
        await self.session.refresh(ticket)
        return ticket

    async def update_ticket_status(self, ticket_id: int, status: TicketStatus):
        ticket = await self.get_ticket_by_id(ticket_id)
        if ticket:
            ticket.status = status
            await self.session.flush()
            return ticket
        return None


class ReservationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_reservation(self, user_id: int, ticket_id: int):
        reservation = Reservation(user_id=user_id, ticket_id=ticket_id, status=ReservationStatus.pending)
        self.session.add(reservation)
        await self.session.flush()
        await self.session.refresh(reservation)
        return reservation

    async def update_reservation_status(self, reservation_id: int, status: ReservationStatus):
        result = await self.session.execute(select(Reservation).filter(Reservation.id == reservation_id))
        reservation = result.scalars().first()
        if reservation:
            reservation.status = status
            await self.session.flush()
            return reservation
        return None
