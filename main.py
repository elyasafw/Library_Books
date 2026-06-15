from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from mysql.connector import Error as MySQLError
from logs.logs_config import logger
from routes.book_routes import router as books_router
from routes.member_routes import router as members_router
from routes.report_routes import router as reports_router
from database.db_connection import DB


app = FastAPI()

@app.exception_handler(MySQLError)
def global_db_error_handler(request: Request, exc: MySQLError):
    logger.error(f"Database Error: {exc.msg} (Code: {exc.errno})") 
    response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    user_message = "Internal server error.. Something went wrong"
    if exc.errno == 1062:
        response_status = status.HTTP_409_CONFLICT
        user_message = "The provided email or unique field already exists"
    elif exc.errno == 1452:
        response_status = status.HTTP_400_BAD_REQUEST
        user_message = "Invalid reference. One of the related records does not exist"
    elif exc.errno == 1265:
        response_status = status.HTTP_422_UNPROCESSABLE_CONTENT
        user_message = "Genre column must be: History / Science / Non-Fiction / Fiction / Other"
    return JSONResponse(
        status_code=response_status,
        content={"detail": user_message}
        )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation failed on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Invalid input data format. Please check your fields"},
        )



@app.exception_handler(Exception)
def global_general_error_handler(request: Request, exc: Exception):
    logger.critical(f"Internal Server Crash: {str(exc)}") 
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
        )


@app.middleware('http')
async def logger_middleware(req: Request, call_next):
    logger.info(f"Method: {req.method} - URL: {req.url}")
    return await call_next(req)

@app.on_event("shutdown")
def shutdown_event():
    DB.close_connection()


app.include_router(books_router)
app.include_router(members_router)
app.include_router(reports_router)