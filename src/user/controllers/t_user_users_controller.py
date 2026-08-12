
import datetime
import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field
from user.models.t_user_users import TUserUsers
from user.daos.t_user_users_dao import TUserUsersDao

router = APIRouter(
    prefix="/api/v1/user/users",
    tags=["api/v1/user/users"],
)


# ====================== 创建参数模型 ======================
class CreateTUserUsers(BaseModel):
    app_id: str | None = Field(default=None, description="渠道ID")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    tel: str | None = Field(default=None, description="联系电话")
    sex: int = Field(default=1, description="性别 0:女 1:男")
    status: int = Field(..., description="状态 0:冻结 1:激活")


class ResponseCreateTUserUsers(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    userid: str = Field(description="新建用户ID")
    request_id: str = Field(description="请求ID")


@router.post("/create", summary="新增用户")
def create(item: CreateTUserUsers) -> ResponseCreateTUserUsers:
    request_id = str(uuid.uuid4())

    # 非空校验
    if not item.username:
        return ResponseCreateTUserUsers(code=204, msg="用户名不能为空", userid="", request_id=request_id)
    if not item.password:
        return ResponseCreateTUserUsers(code=204, msg="密码不能为空", userid="", request_id=request_id)
    if item.status is None:
        return ResponseCreateTUserUsers(code=204, msg="状态不能为空", userid="", request_id=request_id)

    # 唯一校验
    if TUserUsersDao.is_exist("username", item.username):
        return ResponseCreateTUserUsers(code=204, msg="用户名已存在", userid="", request_id=request_id)

    # 组装数据
    model = TUserUsers()
    model.user_id = str(uuid.uuid4())
    model.app_id = item.app_id
    model.username = item.username
    model.password = item.password
    model.tel = item.tel
    model.sex = item.sex
    model.status = item.status
    model.del_flag = 1
    model.create_time = datetime.datetime.now()

    try:
        res = TUserUsersDao.create(model)
        if res:
            return ResponseCreateTUserUsers(code=200, msg="成功", userid=model.user_id, request_id=request_id)
        return ResponseCreateTUserUsers(code=204, msg="创建失败", userid="", request_id=request_id)
    except Exception:
        return ResponseCreateTUserUsers(code=204, msg="创建异常", userid="", request_id=request_id)


# ====================== 修改参数模型 ======================
class ModifyTUserUsers(BaseModel):
    user_id: str = Field(..., description="用户ID")
    app_id: str | None = Field(default=None, description="渠道ID")
    username: str | None = Field(default=None, description="用户名")
    password: str | None = Field(default=None, description="密码")
    tel: str | None = Field(default=None, description="联系电话")
    sex: int | None = Field(default=None, description="性别 0:女 1:男")
    status: int | None = Field(default=None, description="状态 0:冻结 1:激活")


class ResponseModifyTUserUsers(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    request_id: str = Field(description="请求ID")


@router.post("/modify", summary="修改用户")
def modify(item: ModifyTUserUsers) -> ResponseModifyTUserUsers:
    request_id = str(uuid.uuid4())

    if not item.user_id:
        return ResponseModifyTUserUsers(code=204, msg="用户ID不能为空", request_id=request_id)

    model = TUserUsersDao.getbyid(item.user_id)
    if not model:
        return ResponseModifyTUserUsers(code=204, msg="用户ID不存在", request_id=request_id)

    # 动态赋值更新
    if item.app_id is not None:
        model.app_id = item.app_id
    if item.username is not None:
        model.username = item.username
    if item.password is not None:
        model.password = item.password
    if item.tel is not None:
        model.tel = item.tel
    if item.sex is not None:
        model.sex = item.sex
    if item.status is not None:
        model.status = item.status

    model.update_time = datetime.datetime.now()

    try:
        if TUserUsersDao.modify(model):
            return ResponseModifyTUserUsers(code=200, msg="成功", request_id=request_id)
        return ResponseModifyTUserUsers(code=204, msg="修改失败", request_id=request_id)
    except Exception:
        return ResponseModifyTUserUsers(code=204, msg="修改异常", request_id=request_id)


# ====================== 删除接口（逻辑/物理） ======================
class ResponseDeleteTUserUsers(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    request_id: str = Field(description="请求ID")


@router.get("/delete/logic", summary="逻辑删除用户")
def delete_logic(user_id: str) -> ResponseDeleteTUserUsers:
    request_id = str(uuid.uuid4())
    if not user_id:
        return ResponseDeleteTUserUsers(code=204, msg="用户ID不能为空", request_id=request_id)
    if not TUserUsersDao.getbyid(user_id):
        return ResponseDeleteTUserUsers(code=204, msg="用户ID不存在", request_id=request_id)

    try:
        if TUserUsersDao.delete_logic(user_id):
            return ResponseDeleteTUserUsers(code=200, msg="逻辑删除成功", request_id=request_id)
        return ResponseDeleteTUserUsers(code=204, msg="删除失败", request_id=request_id)
    except Exception:
        return ResponseDeleteTUserUsers(code=204, msg="删除异常", request_id=request_id)


@router.get("/delete/physical", summary="物理删除用户")
def delete_physical(user_id: str) -> ResponseDeleteTUserUsers:
    request_id = str(uuid.uuid4())
    if not user_id:
        return ResponseDeleteTUserUsers(code=204, msg="用户ID不能为空", request_id=request_id)
    if not TUserUsersDao.getbyid(user_id):
        return ResponseDeleteTUserUsers(code=204, msg="用户ID不存在", request_id=request_id)

    try:
        if TUserUsersDao.delete_physical(user_id):
            return ResponseDeleteTUserUsers(code=200, msg="物理删除成功", request_id=request_id)
        return ResponseDeleteTUserUsers(code=204, msg="删除失败", request_id=request_id)
    except Exception:
        return ResponseDeleteTUserUsers(code=204, msg="删除异常", request_id=request_id)


# ====================== 单条查询 ======================
class ResponseGetByIDTUserUsers(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    item: dict | None = Field(description="用户数据")
    request_id: str = Field(description="请求ID")


@router.get("/getbyid", summary="根据ID查询用户")
def getbyid(user_id: str) -> ResponseGetByIDTUserUsers:
    request_id = str(uuid.uuid4())
    if not user_id:
        return ResponseGetByIDTUserUsers(code=204, msg="用户ID不能为空", item=None, request_id=request_id)

    try:
        model = TUserUsersDao.getbyid(user_id)
        if model:
            return ResponseGetByIDTUserUsers(code=200, msg="成功", item=model.to_dict(), request_id=request_id)
        return ResponseGetByIDTUserUsers(code=204, msg="数据不存在", item=None, request_id=request_id)
    except Exception:
        return ResponseGetByIDTUserUsers(code=204, msg="查询异常", item=None, request_id=request_id)


# ====================== 查询全部 ======================
class ResponseToList4AllTUserUsers(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    items: list[dict] | None = Field(description="用户列表")
    request_id: str = Field(description="请求ID")


@router.get("/getall", summary="查询所有用户")
def getall() -> ResponseToList4AllTUserUsers:
    request_id = str(uuid.uuid4())
    try:
        data_list = [item.to_dict() for item in TUserUsersDao.tolist4all()]
        return ResponseToList4AllTUserUsers(code=200, msg="成功", items=data_list, request_id=request_id)
    except Exception:
        return ResponseToList4AllTUserUsers(code=204, msg="查询异常", items=None, request_id=request_id)


# ====================== 分页查询 ======================
class PageQueryTUserUsers(BaseModel):
    app_id: str | None = Field(default=None, description="渠道ID")
    username: str | None = Field(default=None, description="用户名")
    tel: str | None = Field(default=None, description="联系电话")
    sex: int | None = Field(default=None, description="性别 0:女 1:男")
    status: int | None = Field(default=None, description="状态 0:冻结 1:激活")
    begin_time: str | None = Field(default=None, description="开始时间")
    end_time: str | None = Field(default=None, description="结束时间")
    page: int = Field(..., description="页码")
    page_size: int = Field(..., description="每页条数")


class ResponsePageTUserUsers(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    total: int = Field(description="总条数")
    items: list[dict] | None = Field(description="用户列表")
    request_id: str = Field(description="请求ID")


@router.post("/get4page", summary="用户分页查询")
def get4page(item: PageQueryTUserUsers) -> ResponsePageTUserUsers:
    request_id = str(uuid.uuid4())

    if not item.page or not item.page_size:
        return ResponsePageTUserUsers(code=204, msg="页码/分页条数不能为空", total=0, items=None, request_id=request_id)

    # 拼接查询条件，默认过滤已逻辑删除数据
    sql = "select * from t_user_users where del_flag = 1 and 1=1"
    if item.app_id:
        sql += f" and app_id = '{item.app_id}'"
    if item.username:
        sql += f" and username like '%{item.username}%'"
    if item.tel:
        sql += f" and tel like '%{item.tel}%'"
    if item.sex is not None:
        sql += f" and sex = {item.sex}"
    if item.status is not None:
        sql += f" and status = {item.status}"
    if item.begin_time:
        sql += f" and create_time >= '{item.begin_time}'"
    if item.end_time:
        sql += f" and create_time <= '{item.end_time}'"

    try:
        data_list, total = TUserUsersDao.tolist4page(item.page, item.page_size, sql, "create_time", "asc")
        res_list = [i.to_dict() for i in data_list]
        return ResponsePageTUserUsers(code=200, msg="成功", total=total, items=res_list, request_id=request_id)
    except Exception:
        return ResponsePageTUserUsers(code=204, msg="分页查询异常", total=0, items=None, request_id=request_id)


# ====================== 唯一性校验 ======================
class ResponseIsExistTUserUsers(BaseModel):
    code: int = Field(description="返回码 200:成功 204:失败")
    msg: str = Field(description="返回信息")
    is_exist: bool = Field(description="是否存在")
    request_id: str = Field(description="请求ID")


@router.get("/is_exist", summary="字段唯一性校验")
def is_exist(field: str, value: str) -> ResponseIsExistTUserUsers:
    request_id = str(uuid.uuid4())
    try:
        flag = TUserUsersDao.is_exist(field, value)
        return ResponseIsExistTUserUsers(code=200, msg="成功", is_exist=flag, request_id=request_id)
    except Exception:
        return ResponseIsExistTUserUsers(code=204, msg="校验异常", is_exist=False, request_id=request_id)