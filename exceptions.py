from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# 1. 필수 파라미터 누락 등 유효성 검사 실패 (400)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": "invalid_request", "data": None}
    )


# 2. 허용되지 않은 메소드 요청 (405) + 기타 HTTP 예외
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 405:
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={"code": "METHOD_NOT_ALLOWED", "data": None}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.detail, "data": None}
    )


# 3. 서버 내부 에러 (500)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": "internal_server_error", "data": None}
    )


# 4. 리소스 없음 (404)
async def not_found_exception_handler(request: Request, exc: Exception = None):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"code": "not_found", "data": None}
    )


def register_exception_handlers(app: FastAPI) -> None:

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)