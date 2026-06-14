from fastapi import APIRouter, HTTPException, status
from .member_routes import MDB
from .book_routes import BDB


router = APIRouter()

@router.get("/reports/summary")
def get_report():
    report = {
        "total_books": BDB.count_total_books(),
        "available_books": BDB.available_books(),
        "currently_borrowed": BDB.count_borrowed_books(),
        "active_members": MDB.count_active_members()
        }
    return report

@router.get("/reports/books-by-genre")
def report_by_genre():
    genre_report = BDB.count_by_genre()
    return genre_report

@router.get("/reports/top-member")
def report_top_member():
    top_member = MDB.get_top_member()
    if top_member:
        return top_member
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Table members is empty"
        )