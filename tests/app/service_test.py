import pytest
import pytest_asyncio
from app.database import get_session, async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import UserService, ConcertService, TicketService, ReservationService
from app.model import TicketStatus, ReservationStatus, create_tables
from datetime import datetime, timezone


@pytest_asyncio.fixture
async def session():
    await create_tables()
    async for s in get_session():
        await s.begin()
        try:
            yield s
        except Exception as e:
            await s.rollback()
            raise e
        finally:
            await s.rollback()

    await async_engine.dispose()


# UserService 테스트
@pytest.mark.asyncio
async def test_사용자_등록(session: AsyncSession):
    user_service = UserService(session)
    user = await user_service.register_user(username="john_doe", email="john@example.com")

    assert user.username == "john_doe"
    assert user.email == "john@example.com"


@pytest.mark.asyncio
async def test_사용자정보_얻기(session: AsyncSession):
    user_service = UserService(session)
    created_user = await user_service.register_user(username="sue_lee", email="sue@example.com")
    user = await user_service.get_user(created_user.id)

    assert user.id == created_user.id
    assert user.username == "sue_lee"
    assert user.email == "sue@example.com"


# ConcertService 테스트
@pytest.mark.asyncio
async def test_콘서트_생성(session: AsyncSession):
    concert_service = ConcertService(session)

    # 콘서트 생성 테스트
    concert = await concert_service.create_concert(name="Live Concert", event_date=datetime.now(timezone.utc))

    # 콘서트가 제대로 생성되었는지 확인
    assert concert.name == "Live Concert"
    assert isinstance(concert.event_date, datetime)


@pytest.mark.asyncio
async def test_콘서트시트_생성(session: AsyncSession):
    concert_service = ConcertService(session)

    # 콘서트 생성
    concert = await concert_service.create_concert(name="Orchestra Night", event_date=datetime.now(timezone.utc))

    # 좌석 생성 테스트
    seats_info = await concert_service.create_concert_seats(concert.id, total_seats=100)

    # 좌석이 제대로 생성되었는지 확인
    assert seats_info == f"100 seats created for concert {concert.id}"


# TicketService 테스트
@pytest.mark.asyncio
async def test_티켓_생성(session: AsyncSession):
    concert_service = ConcertService(session)
    ticket_service = TicketService(session)

    # 콘서트 생성
    concert = await concert_service.create_concert(name="IU Concert", event_date=datetime.now(timezone.utc))

    # 시트 생성
    await concert_service.create_concert_seats(concert.id, total_seats=1)
    seats = await concert_service.get_seats(concert.id)

    # 첫 번째 시트의 seat_id를 사용
    seat = seats[0]  # seats 리스트에서 첫 번째 좌석 가져오기
    seat_id = seat.id  # 해당 좌석의 id 가져오기

    # 티켓 생성 테스트
    ticket = await ticket_service.create_ticket(concert_id=concert.id, seat_id=seat_id, price=100.00)

    # 티켓이 제대로 생성되었는지 확인
    assert ticket.concert_id == concert.id
    assert ticket.seat_id == seat_id
    assert ticket.price == 100.00
    assert ticket.status == TicketStatus.available


@pytest.mark.asyncio
async def test_티켓상태_갱신(session: AsyncSession):
    concert_service = ConcertService(session)
    ticket_service = TicketService(session)

    # 콘서트 생성
    concert = await concert_service.create_concert(name="G-Dragon Concert", event_date=datetime.now(timezone.utc))

    # 시트 생성
    await concert_service.create_concert_seats(concert.id, total_seats=1)
    seats = await concert_service.get_seats(concert.id)

    # 첫 번째 시트의 seat_id를 사용
    seat = seats[0]  # seats 리스트에서 첫 번째 좌석 가져오기
    seat_id = seat.id  # 해당 좌석의 id 가져오기

    # 티켓 생성 테스트
    ticket = await ticket_service.create_ticket(concert_id=concert.id, seat_id=seat_id, price=100.00)
    updated_ticket = await ticket_service.update_ticket_status(ticket.id, TicketStatus.reserved)

    # 티켓 상태가 업데이트되었는지 확인
    assert updated_ticket.status == TicketStatus.reserved


# ReservationService 테스트
@pytest.mark.asyncio
async def test_티켓_예약(session: AsyncSession):
    concert_service = ConcertService(session)
    ticket_service = TicketService(session)
    reservation_service = ReservationService(session)
    user_service = UserService(session)

    # 콘서트 생성
    concert = await concert_service.create_concert(name="BTS Concert", event_date=datetime.now(timezone.utc))

    # 시트 생성
    await concert_service.create_concert_seats(concert.id, total_seats=1)
    seats = await concert_service.get_seats(concert.id)

    # 첫 번째 시트의 seat_id를 사용
    seat = seats[0]  # seats 리스트에서 첫 번째 좌석 가져오기
    seat_id = seat.id  # 해당 좌석의 id 가져오기

    # 티켓 생성 테스트
    user = await user_service.register_user(username="test_user", email="user@example.com")
    ticket = await ticket_service.create_ticket(concert_id=concert.id, seat_id=seat_id, price=100.00)

    # 티켓 예약
    reservation = await reservation_service.reserve_ticket(user_id=user.id, ticket_id=ticket.id)

    # 예약이 제대로 생성되었는지 확인
    assert reservation.user_id == user.id
    assert reservation.ticket_id == ticket.id
    assert reservation.status == ReservationStatus.pending
    assert (await ticket_service.get_ticket_by_id(ticket.id)).status == TicketStatus.reserved


@pytest.mark.asyncio
async def test_티켓예약_확정(session: AsyncSession):
    concert_service = ConcertService(session)
    ticket_service = TicketService(session)
    reservation_service = ReservationService(session)
    user_service = UserService(session)

    # 콘서트 생성
    concert = await concert_service.create_concert(name="BlackPink Concert", event_date=datetime.now(timezone.utc))

    # 시트 생성
    await concert_service.create_concert_seats(concert.id, total_seats=1)
    seats = await concert_service.get_seats(concert.id)

    # 첫 번째 시트의 seat_id를 사용
    seat = seats[0]  # seats 리스트에서 첫 번째 좌석 가져오기
    seat_id = seat.id  # 해당 좌석의 id 가져오기

    # 티켓 생성 테스트
    user = await user_service.register_user(username="test_user", email="user@example.com")
    ticket = await ticket_service.create_ticket(concert_id=concert.id, seat_id=seat_id, price=100.00)

    # 티켓 예약
    reservation = await reservation_service.reserve_ticket(user_id=user.id, ticket_id=ticket.id)

    # 예약 확인
    confirmed_reservation = await reservation_service.confirm_reservation(reservation.id)

    # 예약이 제대로 확인되었는지 확인
    assert confirmed_reservation.status == ReservationStatus.confirmed
    assert (await ticket_service.get_ticket_by_id(ticket.id)).status == TicketStatus.sold
