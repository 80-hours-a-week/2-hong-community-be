from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


# 1. 상세한 유효성 검사 실패 핸들러 (400)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
Pydantic 유효성 검사 에러를 프론트엔드 친화적인 형태로 변환합니다.
각 필드별로 에러 타입, 메시지, 컨텍스트 정보를 제공합니다.
    """
    errors = {}
    for error in exc.errors():
        # location parsing (query, body 등 위치 정보 중 마지막 필드명 추출)
        loc = error.get("loc", [])
        field = str(loc[-1]) if loc else "unknown"
        
        # detail info construction
        detail = {
            "type": error.get("type"),
            "message": error.get("msg"),
        }
        
        # 범위 초과 등 추가 정보(ctx)가 있는 경우 포함
        if "ctx" in error:
            detail["context"] = error["ctx"]

        if field not in errors:
            errors[field] = []
        errors[field].append(detail)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": "VALIDATION_ERROR", "data": errors}
    )


# 2. 통합 HTTP 예외 핸들러 (4xx)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
모든 HTTP 예외(400~499)를 처리합니다.
status_code에 따라 미리 정의된 에러 코드를 반환하거나,
raise HTTPException(status_code=400, detail="CUSTOM_CODE") 처럼 
전달된 detail 메시지를 그대로 코드값으로 사용합니다.
    """
    error_code_map = {
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: "FILE_TOO_LARGE",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "UNPROCESSABLE_ENTITY",
        status.HTTP_429_TOO_MANY_REQUESTS: "TOO_MANY_REQUESTS",
    }
    
    # 매핑된 코드가 있으면 사용, 없으면 detail(커스텀 에러 코드) 사용
    code = error_code_map.get(exc.status_code, exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={"code": code, "data": None}
    )


# 3. 서버 내부 에러 (500)
async def global_exception_handler(request: Request, exc: Exception):
    """
예상치 못한 서버 내부 에러를 처리합니다.
보안을 위해 상세 에러 내용은 숨기고 표준 메시지만 반환합니다.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": "INTERNAL_SERVER_ERROR", "data": None}
    )


def register_exception_handlers(app: FastAPI) -> None:
    # 유효성 검사 에러 (Pydantic)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 일반 HTTP 에러 (Starlette/FastAPI)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # 기타 서버 에러 (Python Exception)
    app.add_exception_handler(Exception, global_exception_handler)