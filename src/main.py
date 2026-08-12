from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi2 import fastapi2_dbs, fastapi2_routes
# 导入自定义异常处理器
from fastapi2.exception_handler import custom_validation_exception_handler, custom_json_decode_exception_handler, global_exception_handler
import json

# 初始化FastAPI应用
app = FastAPI()


# 初始化数据库
fastapi2_dbs.init_dbs()
# 初始化路由
fastapi2_routes.init_routes(app)


# 注册异常处理器（覆盖默认响应）*必须导入
# 1. 注册 JSON 解析错误 + 参数校验错误处理器
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)
# 2. 注册底层 JSONDecodeError 处理器（确保无遗漏）
app.add_exception_handler(json.JSONDecodeError, custom_json_decode_exception_handler)
# 3. 注册全局异常处理器（兜底 500 错误）
app.add_exception_handler(Exception, global_exception_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


# 访问地址：http://127.0.0.1:8080/docs
# 常用命令
# uv pip freeze > requirements.txt
# uv pip install -r requirements.txt
# uv pip download -r requirements.txt -d ./vendor
# uv pip install --no-index --find-links=./vendor -r requirements.txt

# uv pip install uvicorn fastapi sqlalchemy pymysql pytest
# uv pip install redis
