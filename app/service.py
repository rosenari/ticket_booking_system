from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import (
    UserRepository, ConcertRepository, TicketRepository, ReservationRepository,
    ReservationStatus, TicketStatus
)
from app.util import transactional


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    @transactional
    async def register_user(self, username: str, email: str):
        return await self.user_repo.create_user(username, email)

    async def get_user(self, user_id: int):
        return await self.user_repo.get_user_by_id(user_id)


class ConcertService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.concert_repo = ConcertRepository(session)

    async def get_seats(self, concert_id: int):
        return await self.concert_repo.get_seats_by_concert_id(concert_id=concert_id)

    @transactional
    async def create_concert(self, name: str, event_date):
        return await self.concert_repo.create_concert(name, event_date)

    @transactional
    async def create_concert_seats(self, concert_id: int, total_seats: int):
        return await self.concert_repo.create_seats(concert_id, total_seats)


class TicketService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ticket_repo = TicketRepository(session)

    async def get_ticket_by_id(self, ticket_id: int):
        return await self.ticket_repo.get_ticket_by_id(ticket_id)

    @transactional
    async def create_ticket(self, concert_id: int, seat_id: int, price: float):
        return await self.ticket_repo.create_ticket(concert_id, seat_id, price)

    @transactional
    async def update_ticket_status(self, ticket_id: int, status):
        return await self.ticket_repo.update_ticket_status(ticket_id, status)


class ReservationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.reservation_repo = ReservationRepository(session)
        self.ticket_service = TicketService(session)

    @transactional
    async def reserve_ticket(self, user_id: int, ticket_id: int):
        # TicketService를 통해 티켓 상태 확인 및 상태 업데이트
        ticket = await self.ticket_service.get_ticket_by_id(ticket_id)
        if ticket and ticket.status == TicketStatus.available:
            # 예약 생성
            reservation = await self.reservation_repo.create_reservation(user_id, ticket_id)
            # 티켓을 'reserved' 상태로 업데이트
            await self.ticket_service.update_ticket_status(ticket_id, TicketStatus.reserved)
            return reservation
        return None

    @transactional
    async def confirm_reservation(self, reservation_id: int):
        # 예약 상태를 'confirmed'로 업데이트
        reservation = await self.reservation_repo.update_reservation_status(reservation_id, ReservationStatus.confirmed)
        if reservation:
            # 티켓을 'sold' 상태로 업데이트
            await self.ticket_service.update_ticket_status(reservation.ticket_id, TicketStatus.sold)
        return reservation
