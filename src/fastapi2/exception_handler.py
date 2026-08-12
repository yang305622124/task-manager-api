from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import json
from uuid import uuid4
from typing import Dict, Any

# 统一错误响应格式（与你的自定义返回类型对齐）
def create_error_response(code: int, msg: str,data: Any = None) -> Dict[str, Any]:
    """生成统一格式的错误响应"""
    return {
        "code": code,
        "msg": msg,
        "data": data,
        "request_id": str(uuid4())  # 每个错误分配唯一请求ID，便于排查
    }

# 1. 处理 JSON 解析错误 + 参数校验错误
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    # 判断是否为 JSON 解析错误（json_invalid）
    if any(error["type"] == "json_invalid" for error in exc.errors()):
        return JSONResponse(
            status_code=400,
            content=create_error_response(
                code=400,
                msg=f"JSON 格式错误：{exc.errors()[0]['ctx']['error']}"  # 显示具体解析错误（如缺少逗号）
            )
        )
    # 其他参数校验错误（如字段类型、必填项等）
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            code=422,
            msg="参数校验失败",
            data=exc.errors()  # 返回详细的参数错误信息
        )
    )

# 2. 处理底层 JSONDecodeError（确保全覆盖）
async def custom_json_decode_exception_handler(request: Request, exc: json.JSONDecodeError):
    return JSONResponse(
        status_code=400,
        content=create_error_response(
            code=400,
            msg=f"JSON 解析失败：{str(exc)}"  # 显示具体错误位置（如第39字符缺少逗号）
        )
    )

# 3. 处理 500 服务器内部错误（全局异常兜底）
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            code=500,
            msg=f"服务器内部错误：{str(exc)}"  # 生产环境可改为 "服务器繁忙，请稍后重试"
        )
    )