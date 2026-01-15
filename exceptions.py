from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# 1. 필수 파라미터 누락 등 유효성 검사 실패 (400)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # HACK (임시): ValidationError에서 필드별 오류 메시지 수집
    errors = {}
    for error in exc.errors():
        field = str(error["loc"][-1])
        msg = error["msg"]
        if field not in errors:
            errors[field] = []
        errors[field].append(msg)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": "BAD_REQUEST", "data": errors}
    )

# 2. 인증 필요 (401)
async def unauthorized_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"code": "UNAUTHORIZED", "data": None}
    )

# 3. 접근 권한 없음 (403)
async def forbidden_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"code": "FORBIDDEN", "data": None}
    )

# 4. 리소스 없음 (404)
async def not_found_exception_handler(request: Request, exc: Exception = None):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"code": "NOT_FOUND", "data": None}
    )

# 5. 허용되지 않은 메서드 (405)
async def method_not_allowed_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        content={"code": "METHOD_NOT_ALLOWED", "data": None}
    )

# 6. 리소스 충돌 (409)
async def conflict_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"code": "CONFLICT", "data": None}
    )

# 7. 요청 크기 초과 (413)
async def file_too_large_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content={"code": "FILE_TOO_LARGE", "data": None}
    )

# 8. 처리 불가 요청 (422)
async def unprocessable_entity_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"code": "UNPROCESSABLE_ENTITY", "data": None}
    )

# 9. 요청 과다 (429)
async def too_many_requests_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"code": "TOO_MANY_REQUESTS", "data": None}
    )

# 기타 HTTP 예외
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.detail, "data": None}
    )


# 10. 서버 내부 에러 (500)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": "INTERNAL_SERVER_ERROR", "data": None}
    )


def register_exception_handlers(app: FastAPI) -> None:

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    app.add_exception_handler(status.HTTP_401_UNAUTHORIZED, unauthorized_exception_handler)
    app.add_exception_handler(status.HTTP_403_FORBIDDEN, forbidden_exception_handler)
    app.add_exception_handler(status.HTTP_405_METHOD_NOT_ALLOWED, method_not_allowed_exception_handler)
    app.add_exception_handler(status.HTTP_409_CONFLICT, conflict_exception_handler)
    app.add_exception_handler(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, file_too_large_exception_handler)
    app.add_exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY, unprocessable_entity_exception_handler)
    app.add_exception_handler(status.HTTP_429_TOO_MANY_REQUESTS, too_many_requests_exception_handler)
    
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)