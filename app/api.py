from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from service import ReservationService, UserService, ConcertService

app = FastAPI()


@app.post("/register/")
async def register_user(username: str, email: str, session: AsyncSession = Depends(get_session)):
    user_service = UserService(session)
    return await user_service.register_user(username, email)


@app.post("/concerts/")
async def create_concert(name: str, event_date: str, total_seats: int, session: AsyncSession = Depends(get_session)):
    concert_service = ConcertService(session)
    concert = await concert_service.create_concert(name, event_date)
    return await concert_service.create_concert_seats(concert.id, total_seats)


@app.post("/reserve/")
async def reserve_ticket(user_id: int, ticket_id: int, session: AsyncSession = Depends(get_session)):
    reservation_service = ReservationService(session)
    return await reservation_service.reserve_ticket(user_id, ticket_id)
