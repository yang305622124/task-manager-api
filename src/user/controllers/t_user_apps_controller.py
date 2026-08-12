
import datetime
import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field
from user.models.t_user_apps import TUserApps
from user.daos.t_user_apps_dao import TUserAppsDao

router = APIRouter(
    prefix="/api/v1/user/apps",
    tags=["api/v1/user/apps"],
)


# ====================== 创建参数模型 ======================
class CreateTUserApps(BaseModel):
    name: str = Field(..., description="渠道名称")
    status: int = Field(..., description="状态 0:冻结 1:激活")


class ResponseCreateTUserApps(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    appid: str = Field(description="新建渠道ID")
    request_id: str = Field(description="请求ID")


@router.post("/create", summary="新增渠道")
def create(item: CreateTUserApps) -> ResponseCreateTUserApps:
    request_id = str(uuid.uuid4())

    # 非空校验
    if not item.name:
        return ResponseCreateTUserApps(code=204, msg="渠道名称不能为空", appid="", request_id=request_id)
    if item.status is None:
        return ResponseCreateTUserApps(code=204, msg="状态不能为空", appid="", request_id=request_id)

    # 唯一校验
    if TUserAppsDao.is_exist("name", item.name):
        return ResponseCreateTUserApps(code=204, msg="渠道名称已存在", appid="", request_id=request_id)

    # 组装数据
    model = TUserApps()
    model.app_id = str(uuid.uuid4())
    model.name = item.name
    model.status = item.status
    model.del_flag = 1
    model.create_time = datetime.datetime.now()

    try:
        res = TUserAppsDao.create(model)
        if res:
            return ResponseCreateTUserApps(code=200, msg="成功", appid=model.app_id, request_id=request_id)
        return ResponseCreateTUserApps(code=204, msg="创建失败", appid="", request_id=request_id)
    except Exception:
        return ResponseCreateTUserApps(code=204, msg="创建异常", appid="", request_id=request_id)


# ====================== 修改参数模型 ======================
class ModifyTUserApps(BaseModel):
    app_id: str = Field(..., description="渠道ID")
    name: str | None = Field(default=None, description="渠道名称")
    status: int | None = Field(default=None, description="状态 0:冻结 1:激活")


class ResponseModifyTUserApps(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    request_id: str = Field(description="请求ID")


@router.post("/modify", summary="修改渠道")
def modify(item: ModifyTUserApps) -> ResponseModifyTUserApps:
    request_id = str(uuid.uuid4())

    if not item.app_id:
        return ResponseModifyTUserApps(code=204, msg="渠道ID不能为空", request_id=request_id)

    model = TUserAppsDao.getbyid(item.app_id)
    if not model:
        return ResponseModifyTUserApps(code=204, msg="渠道ID不存在", request_id=request_id)

    # 动态赋值更新
    if item.name is not None:
        model.name = item.name
    if item.status is not None:
        model.status = item.status

    model.update_time = datetime.datetime.now()

    try:
        if TUserAppsDao.modify(model):
            return ResponseModifyTUserApps(code=200, msg="成功", request_id=request_id)
        return ResponseModifyTUserApps(code=204, msg="修改失败", request_id=request_id)
    except Exception:
        return ResponseModifyTUserApps(code=204, msg="修改异常", request_id=request_id)


# ====================== 删除接口（逻辑/物理） ======================
class ResponseDeleteTUserApps(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    request_id: str = Field(description="请求ID")


@router.get("/delete/logic", summary="逻辑删除渠道")
def delete_logic(app_id: str) -> ResponseDeleteTUserApps:
    request_id = str(uuid.uuid4())
    if not app_id:
        return ResponseDeleteTUserApps(code=204, msg="渠道ID不能为空", request_id=request_id)
    if not TUserAppsDao.getbyid(app_id):
        return ResponseDeleteTUserApps(code=204, msg="渠道ID不存在", request_id=request_id)

    try:
        if TUserAppsDao.delete_logic(app_id):
            return ResponseDeleteTUserApps(code=200, msg="逻辑删除成功", request_id=request_id)
        return ResponseDeleteTUserApps(code=204, msg="删除失败", request_id=request_id)
    except Exception:
        return ResponseDeleteTUserApps(code=204, msg="删除异常", request_id=request_id)


@router.get("/delete/physical", summary="物理删除渠道")
def delete_physical(app_id: str) -> ResponseDeleteTUserApps:
    request_id = str(uuid.uuid4())
    if not app_id:
        return ResponseDeleteTUserApps(code=204, msg="渠道ID不能为空", request_id=request_id)
    if not TUserAppsDao.getbyid(app_id):
        return ResponseDeleteTUserApps(code=204, msg="渠道ID不存在", request_id=request_id)

    try:
        if TUserAppsDao.delete_physical(app_id):
            return ResponseDeleteTUserApps(code=200, msg="物理删除成功", request_id=request_id)
        return ResponseDeleteTUserApps(code=204, msg="删除失败", request_id=request_id)
    except Exception:
        return ResponseDeleteTUserApps(code=204, msg="删除异常", request_id=request_id)


# ====================== 单条查询 ======================
class ResponseGetByIDTUserApps(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    item: dict | None = Field(description="渠道数据")
    request_id: str = Field(description="请求ID")


@router.get("/getbyid", summary="根据ID查询渠道")
def getbyid(app_id: str) -> ResponseGetByIDTUserApps:
    request_id = str(uuid.uuid4())
    if not app_id:
        return ResponseGetByIDTUserApps(code=204, msg="渠道ID不能为空", item=None, request_id=request_id)

    try:
        model = TUserAppsDao.getbyid(app_id)
        if model:
            return ResponseGetByIDTUserApps(code=200, msg="成功", item=model.to_dict(), request_id=request_id)
        return ResponseGetByIDTUserApps(code=204, msg="数据不存在", item=None, request_id=request_id)
    except Exception:
        return ResponseGetByIDTUserApps(code=204, msg="查询异常", item=None, request_id=request_id)


# ====================== 查询全部 ======================
class ResponseToList4AllTUserApps(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    items: list[dict] | None = Field(description="渠道列表")
    request_id: str = Field(description="请求ID")


@router.get("/getall", summary="查询所有渠道")
def getall() -> ResponseToList4AllTUserApps:
    request_id = str(uuid.uuid4())
    try:
        data_list = [item.to_dict() for item in TUserAppsDao.tolist4all()]
        return ResponseToList4AllTUserApps(code=200, msg="成功", items=data_list, request_id=request_id)
    except Exception:
        return ResponseToList4AllTUserApps(code=204, msg="查询异常", items=None, request_id=request_id)


# ====================== 分页查询 ======================
class PageQueryTUserApps(BaseModel):
    name: str | None = Field(default=None, description="渠道名称")
    status: int | None = Field(default=None, description="状态 0:冻结 1:激活")
    begin_time: str | None = Field(default=None, description="开始时间")
    end_time: str | None = Field(default=None, description="结束时间")
    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页条数")


class ResponsePageTUserApps(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    total: int = Field(description="总条数")
    items: list[dict] | None = Field(description="渠道列表")
    request_id: str = Field(description="请求ID")


@router.post("/get4page", summary="渠道分页查询")
def get4page(item: PageQueryTUserApps) -> ResponsePageTUserApps:
    request_id = str(uuid.uuid4())

    if not item.page or not item.page_size:
        return ResponsePageTUserApps(code=204, msg="页码/分页条数不能为空", total=0, items=None, request_id=request_id)

    # 拼接查询条件
    sql = "select * from t_user_apps where del_flag = 1 and 1=1"
    if item.name:
        sql += f" and name like '%{item.name}%'"
    if item.status is not None:
        sql += f" and status = {item.status}"
    if item.begin_time:
        sql += f" and create_time >= '{item.begin_time}'"
    if item.end_time:
        sql += f" and create_time <= '{item.end_time}'"

    try:
        data_list, total = TUserAppsDao.tolist4page(item.page, item.page_size, sql, "create_time", "asc")
        res_list = [i.to_dict() for i in data_list]
        return ResponsePageTUserApps(code=200, msg="成功", total=total, items=res_list, request_id=request_id)
    except Exception:
        return ResponsePageTUserApps(code=204, msg="分页查询异常", total=0, items=None, request_id=request_id)


# ====================== 唯一性校验 ======================
class ResponseIsExistTUserApps(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    is_exist: bool = Field(description="是否存在")
    request_id: str = Field(description="请求ID")


@router.get("/is_exist", summary="字段唯一性校验")
def is_exist(field: str, value: str) -> ResponseIsExistTUserApps:
    request_id = str(uuid.uuid4())
    try:
        flag = TUserAppsDao.is_exist(field, value)
        return ResponseIsExistTUserApps(code=200, msg="成功", is_exist=flag, request_id=request_id)
    except Exception:
        return ResponseIsExistTUserApps(code=204, msg="校验异常", is_exist=False, request_id=request_id)
