from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from database import book_db as book, member_db as member
from logs.logs_config import logger


class NewBook(BaseModel):
    title: str
    author: str
    genre: str

class UpdateBook(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None


BDB = book.BooksDB()
MDB = member.MemberDB()


router = APIRouter()

@router.post("/books", status_code=status.HTTP_201_CREATED)
def create_new_book(new_book: NewBook):
        book_data = new_book.model_dump()
        success_create =  BDB.create_book(book_data)
        if success_create:
            return success_create
        return {"message": "created book failed"}

@router.get("/books")
def get_all_books_in_table():
        all_books = BDB.get_all_books()
        if all_books:
            return all_books
        return {"message": "books list is empty"}

@router.get("/books/{id}")
def get_book_by_id(id: int):
    book = BDB.get_book_by_id()
    if book:
        return book
    return {"message": "book not found"}

@router.patch("/books/{id}")
def update_book(id: int, update_data: UpdateBook):
    changes = update_data.model_dump(exclude_unset=True)
    if not changes:
        logger.warning("Book data update is empty..  No changes")
        return {"message": "data is empty..."}
    success_update = BDB.update_book(id, changes)
    if success_update:
        return success_update
    return {"message": "update book failed"}

@router.patch("/books/{id}/borrow/{member_id}")
def borrow_book(id: int, member_id: int):
    member = MDB.get_member_by_id(member_id)
    if member:
        if member["is_active"] == True:
            count_borrows = BDB.count_active_borrow_by_member(member_id)
        else:
            logger.warning(f"Member ID: {member_id} is not active")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "member is not active"}
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "member does not exists"}
            )
    if count_borrows == 3:
        book = BDB.get_book_by_id(id)
    else:
        logger.warning("Member has reached = 3 borrows")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "member has reached maximum borrows"}
            )
    if book:
        if book["is_available"] == True:
            val = False
            borrowed_book = BDB.set_available(id, val, member_id)
            MDB.increment_borrows(member_id)
            return borrowed_book
        else:
            logger.warning(f"Book ID: {id} not available")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "book is not available"}
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "book does not exists"}
            )

@router("/books/{id}/return/{member_id}")
def return_book(id:int, member_id: int):
    member = MDB.get_member_by_id(member_id)
    if member:
            book = BDB.get_book_by_id(id)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "member does not exists"}
            )
    if book:
        if book["is_available"] == False:
            if book["borrowed_by_member_id"] == member_id:
                val = True
                member_id = None
                returned_book = BDB.set_available(id, val, member_id)
                return returned_book
            else:
                logger.warning(f"Book ID: {id} not borrow by member ID: {member_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": "book is not available"}
                    )
        else:
            logger.warning(f"Book ID: {id} not borrow")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "book is not borrow"}
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "book does not exists"}
            )