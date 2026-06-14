from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from mysql.connector import Error as MySQLError
from logs.logs_config import logger
from routes.book_routes import router as book_router


app = FastAPI()

@app.exception_handler(MySQLError)
def global_db_error_handler(request: Request, exc: MySQLError):
    logger.error(f"Database Error: {exc.msg} (Code: {exc.errno})") 
    
    response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    user_message = "Internal server error"

    if exc.errno == 1062:
        response_status = status.HTTP_409_CONFLICT
        user_message = "The provided email or unique field already exists."
        
    elif exc.errno == 1452:
        response_status = status.HTTP_400_BAD_REQUEST
        user_message = "Invalid reference. One of the related records does not exist."

    return JSONResponse(
        status_code=response_status,
        content={"detail": user_message}
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
    logger.info(req.url, req.method)
    return await call_next()