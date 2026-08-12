
import uuid
from fastapi.testclient import TestClient
from main import app  # 请根据自己项目入口调整

# 挂载测试客户端
client = TestClient(app)

# 统一接口前缀
API_PREFIX = "/api/v1/user/users"

# 全局测试变量
test_username = f"test_user_{str(uuid.uuid4())[:8]}"
test_user_id = ""


class TestTUserUsersController:
    """用户 t_user_users 单元测试（全覆盖所有接口分支）"""

    def test_01_create_success(self):
        """测试【新增用户-成功场景】"""
        global test_user_id
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "username": test_username,
                "password": "123456",
                "tel": "13800138000",
                "sex": 1,
                "status": 1
            }
        )
        data = res.json()
        assert res.status_code == 200
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert data["userid"] != ""
        assert data["request_id"] != ""
        test_user_id = data["userid"]

    def test_02_create_username_empty(self):
        """测试【新增用户-用户名为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "username": "",
                "password": "123456",
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "用户名不能为空"

    def test_03_create_password_empty(self):
        """测试【新增用户-密码为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "username": test_username + "pwd",
                "password": "",
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "密码不能为空"

    def test_04_create_status_empty(self):
        """测试【新增用户-状态为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "username": test_username + "status",
                "password": "123456",
                "status": None
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "状态不能为空"

    def test_05_create_username_exist(self):
        """测试【新增用户-用户名重复-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "username": test_username,
                "password": "123456",
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "用户名已存在"

    def test_06_modify_success(self):
        """测试【修改用户-成功】"""
        new_tel = "13900139000"
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "user_id": test_user_id,
                "tel": new_tel,
                "status": 0
            }
        )
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"

    def test_07_modify_userid_empty(self):
        """测试【修改用户-user_id为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "user_id": "",
                "username": "testmodify",
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "用户ID不能为空"

    def test_08_modify_userid_not_exist(self):
        """测试【修改用户-user_id不存在-失败】"""
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "user_id": str(uuid.uuid4()),
                "username": "notexist",
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "用户ID不存在"

    def test_09_get_by_id_success(self):
        """测试【根据ID查询用户-成功】"""
        res = client.get(f"{API_PREFIX}/getbyid?user_id={test_user_id}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert data["item"] is not None
        assert data["item"]["user_id"] == test_user_id
        # 密码字段脱敏校验，接口不返回密码
        assert "password" not in data["item"]

    def test_10_get_by_id_empty(self):
        """测试【根据ID查询-user_id为空-失败】"""
        res = client.get(f"{API_PREFIX}/getbyid?user_id=")
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "用户ID不能为空"

    def test_11_get_all(self):
        """测试【查询所有用户】"""
        res = client.get(f"{API_PREFIX}/getall")
        data = res.json()
        assert data["code"] == 200
        assert isinstance(data["items"], list)

    def test_12_page_query(self):
        """测试【用户分页查询-正常条件】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "username": "",
                "tel": "",
                "sex": None,
                "status": None,
                "begin_time": "",
                "end_time": "",
                "page": 1,
                "page_size": 10
            }
        )
        data = res.json()
        assert data["code"] == 200
        assert "total" in data
        assert "items" in data

    def test_13_page_param_empty(self):
        """测试【用户分页参数为空校验】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "page": 0,
                "page_size": 0
            }
        )
        data = res.json()
        assert data["code"] == 204

    def test_14_is_exist_true(self):
        """测试【用户字段存在校验-存在】"""
        res = client.get(f"{API_PREFIX}/is_exist?field=username&value={test_username}")
        data = res.json()
        assert data["code"] == 200
        assert data["is_exist"] is True

    def test_15_is_exist_false(self):
        """测试【用户字段存在校验-不存在】"""
        res = client.get(f"{API_PREFIX}/is_exist?field=username&value={str(uuid.uuid4())}")
        data = res.json()
        assert data["code"] == 200
        assert data["is_exist"] is False

    def test_16_logic_delete(self):
        """测试【用户逻辑删除-成功】"""
        res = client.get(f"{API_PREFIX}/delete/logic?user_id={test_user_id}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "逻辑删除成功"

    def test_17_logic_delete_not_exist(self):
        """测试【用户逻辑删除-ID不存在】"""
        res = client.get(f"{API_PREFIX}/delete/logic?user_id={str(uuid.uuid4())}")
        data = res.json()
        assert data["code"] == 204

    def test_18_physical_delete(self):
        """测试【用户物理删除-成功】"""
        res = client.get(f"{API_PREFIX}/delete/physical?user_id={test_user_id}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "物理删除成功"

    def test_19_physical_delete_empty(self):
        """测试【用户物理删除-ID为空】"""
        res = client.get(f"{API_PREFIX}/delete/physical?user_id=")
        data = res.json()
        assert data["code"] == 204
