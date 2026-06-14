from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, EmailStr
from database import member_db as member
from logs.logs_config import logger


class NewMember(BaseModel):
    name: str
    email: EmailStr


class UpdateMember(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


MDB = member.MemberDB()


router = APIRouter()

@router.post("/members", status_code=status.HTTP_201_CREATED)
def create_new_member(new_member: NewMember):
    member_data = new_member.model_dump()
    success_create =  MDB.create_member(member_data)
    if success_create:
        return success_create
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="created new member is failed"
        )

@router.get("/members")
def get_all_members_in_table():
    all_members = MDB.get_all_members()
    if all_members:
        return all_members
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="books list is empty"
        )

@router.get("/members/{id}")
def get_member_by_id(id: int):
    member = MDB.get_member_by_id(id)
    if member:
        return member
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"member ID: {id} not found"
        )

@router.patch("/members/{id}")
def update_member(id: int, update_data: UpdateMember):
    changes = update_data.model_dump(exclude_unset=True)
    if not changes:
        logger.warning("Member data update is empty..  No changes")
        return {"message": "data is empty..."}
    success_update = MDB.update_member(id, changes)
    if success_update:
        return {"message": f"update successfully: {success_update}"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Update failed. Member ID: {id} not found / no new changes were provided"
        )

@router.patch("/members/{id}/deactivate")
def deactivate_member(id: int):
    success_deactivate = MDB.deactivate_member(id)
    if success_deactivate:
        return {"message": "member deactivated successfully"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"deactivate member is failed, Member ID: {id} not found"
        )

@router.patch("/members/{id}/activate")
def activate_member(id: int):
    success_activate = MDB.activate_member(id)
    if success_activate:
        return {"message": "member activated successfully"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"activate member is failed, Member ID: {id} not found"
        )