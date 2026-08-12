
import datetime
import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field
from task_manager_api.models.task import Task
from task_manager_api.daos.task_dao import TaskDao

router = APIRouter(
    prefix="/api/v1/task",
    tags=["api/v1/task"],
)


# ====================== 创建参数模型 ======================
class CreateTask(BaseModel):
    title: str = Field(..., description="任务标题")
    description: str | None = Field(default=None, description="任务描述")
    status: str = Field(default="todo", description="状态(todo | in_progress | done)")


class ResponseCreateTask(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    task_id: str = Field(description="新建任务ID")
    request_id: str = Field(description="请求ID")


@router.post("/create", summary="新增任务")
def create(item: CreateTask) -> ResponseCreateTask:
    request_id = str(uuid.uuid4())

    # 非空校验
    if not item.title:
        return ResponseCreateTask(code=204, msg="任务标题不能为空", task_id="", request_id=request_id)

    # 唯一校验
    if TaskDao.is_exist("title", item.title):
        return ResponseCreateTask(code=204, msg="任务标题已存在", task_id="", request_id=request_id)

    # 组装数据
    model = Task()
    model.id = str(uuid.uuid4())
    model.title = item.title
    model.description = item.description
    model.status = item.status
    model.created_at = datetime.datetime.now()

    try:
        res = TaskDao.create(model)
        if res:
            return ResponseCreateTask(code=200, msg="成功", task_id=model.id, request_id=request_id)
        return ResponseCreateTask(code=204, msg="创建失败", task_id="", request_id=request_id)
    except Exception:
        return ResponseCreateTask(code=204, msg="创建异常", task_id="", request_id=request_id)


# ====================== 修改参数模型 ======================
class ModifyTask(BaseModel):
    id: str = Field(..., description="任务ID")
    title: str | None = Field(default=None, description="任务标题")
    description: str | None = Field(default=None, description="任务描述")
    status: str | None = Field(default=None, description="状态(todo | in_progress | done)")


class ResponseModifyTask(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    request_id: str = Field(description="请求ID")


@router.post("/modify", summary="修改任务")
def modify(item: ModifyTask) -> ResponseModifyTask:
    request_id = str(uuid.uuid4())

    if not item.id:
        return ResponseModifyTask(code=204, msg="任务ID不能为空", request_id=request_id)

    model = TaskDao.getbyid(item.id)
    if not model:
        return ResponseModifyTask(code=204, msg="任务ID不存在", request_id=request_id)

    # 动态赋值更新
    if item.title is not None:
        model.title = item.title
    if item.description is not None:
        model.description = item.description
    if item.status is not None:
        model.status = item.status

    model.updated_at = datetime.datetime.now()

    try:
        if TaskDao.modify(model):
            return ResponseModifyTask(code=200, msg="成功", request_id=request_id)
        return ResponseModifyTask(code=204, msg="修改失败", request_id=request_id)
    except Exception:
        return ResponseModifyTask(code=204, msg="修改异常", request_id=request_id)


# ====================== 删除接口（物理） ======================
class ResponseDeleteTask(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    request_id: str = Field(description="请求ID")


@router.get("/delete/physical", summary="物理删除任务")
def delete_physical(id: str) -> ResponseDeleteTask:
    request_id = str(uuid.uuid4())
    if not id:
        return ResponseDeleteTask(code=204, msg="任务ID不能为空", request_id=request_id)
    if not TaskDao.getbyid(id):
        return ResponseDeleteTask(code=204, msg="任务ID不存在", request_id=request_id)

    try:
        if TaskDao.delete_physical(id):
            return ResponseDeleteTask(code=200, msg="物理删除成功", request_id=request_id)
        return ResponseDeleteTask(code=204, msg="删除失败", request_id=request_id)
    except Exception:
        return ResponseDeleteTask(code=204, msg="删除异常", request_id=request_id)


# ====================== 单条查询 ======================
class ResponseGetByIDTask(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    item: dict | None = Field(description="任务数据")
    request_id: str = Field(description="请求ID")


@router.get("/getbyid", summary="根据ID查询任务")
def getbyid(id: str) -> ResponseGetByIDTask:
    request_id = str(uuid.uuid4())
    if not id:
        return ResponseGetByIDTask(code=204, msg="任务ID不能为空", item=None, request_id=request_id)

    try:
        model = TaskDao.getbyid(id)
        if model:
            return ResponseGetByIDTask(code=200, msg="成功", item=model.to_dict(), request_id=request_id)
        return ResponseGetByIDTask(code=204, msg="数据不存在", item=None, request_id=request_id)
    except Exception:
        return ResponseGetByIDTask(code=204, msg="查询异常", item=None, request_id=request_id)


# ====================== 查询全部 ======================
class ResponseToList4AllTask(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    items: list[dict] | None = Field(description="任务列表")
    request_id: str = Field(description="请求ID")


@router.get("/getall", summary="查询所有任务")
def getall() -> ResponseToList4AllTask:
    request_id = str(uuid.uuid4())
    try:
        data_list = [item.to_dict() for item in TaskDao.tolist4all()]
        return ResponseToList4AllTask(code=200, msg="成功", items=data_list, request_id=request_id)
    except Exception:
        return ResponseToList4AllTask(code=204, msg="查询异常", items=None, request_id=request_id)


# ====================== 分页查询 ======================
class PageQueryTask(BaseModel):
    title: str | None = Field(default=None, description="任务标题")
    status: str | None = Field(default=None, description="状态(todo | in_progress | done)")
    begin_time: str | None = Field(default=None, description="开始时间")
    end_time: str | None = Field(default=None, description="结束时间")
    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页条数")


class ResponsePageTask(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    total: int = Field(description="总条数")
    items: list[dict] | None = Field(description="任务列表")
    request_id: str = Field(description="请求ID")


@router.post("/get4page", summary="任务分页查询")
def get4page(item: PageQueryTask) -> ResponsePageTask:
    request_id = str(uuid.uuid4())

    if not item.page or not item.page_size:
        return ResponsePageTask(code=204, msg="页码/分页条数不能为空", total=0, items=None, request_id=request_id)

    # 拼接查询条件
    sql = "select * from task where 1=1"
    if item.title:
        sql += f" and title like '%{item.title}%'"
    if item.status:
        sql += f" and status = '{item.status}'"
    if item.begin_time:
        sql += f" and created_at >= '{item.begin_time}'"
    if item.end_time:
        sql += f" and created_at <= '{item.end_time}'"

    try:
        data_list, total = TaskDao.tolist4page(item.page, item.page_size, sql, "created_at", "asc")
        res_list = [i.to_dict() for i in data_list]
        return ResponsePageTask(code=200, msg="成功", total=total, items=res_list, request_id=request_id)
    except Exception:
        return ResponsePageTask(code=204, msg="分页查询异常", total=0, items=None, request_id=request_id)


# ====================== 唯一性校验 ======================
class ResponseIsExistTask(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    is_exist: bool = Field(description="是否存在")
    request_id: str = Field(description="请求ID")


@router.get("/is_exist", summary="字段唯一性校验")
def is_exist(field: str, value: str) -> ResponseIsExistTask:
    request_id = str(uuid.uuid4())
    try:
        flag = TaskDao.is_exist(field, value)
        return ResponseIsExistTask(code=200, msg="成功", is_exist=flag, request_id=request_id)
    except Exception:
        return ResponseIsExistTask(code=204, msg="校验异常", is_exist=False, request_id=request_id)
