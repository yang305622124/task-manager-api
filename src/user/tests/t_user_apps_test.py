
import uuid
from fastapi.testclient import TestClient
from main import app  # 请根据自己项目入口调整

# 挂载测试客户端
client = TestClient(app)

# 统一接口前缀
API_PREFIX = "/api/v1/user/apps"

# 全局测试变量
test_app_name = f"test_{str(uuid.uuid4())[:8]}"
test_app_id = ""


class TestTUserAppsController:
    """渠道应用 t_user_apps 单元测试（全覆盖所有接口分支）"""

    def test_01_create_success(self):
        """测试【新增渠道-成功场景】"""
        global test_app_id
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "name": test_app_name,
                "status": 1
            }
        )
        data = res.json()
        assert res.status_code == 200
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert data["appid"] != ""
        assert data["request_id"] != ""
        test_app_id = data["appid"]

    def test_02_create_name_empty(self):
        """测试【新增渠道-name为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "name": "",
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "渠道名称不能为空"

    def test_03_create_status_empty(self):
        """测试【新增渠道-status为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "name": test_app_name + "111",
                "status": None
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "状态不能为空"

    def test_04_create_name_exist(self):
        """测试【新增渠道-名称重复-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "name": test_app_name,
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "渠道名称已存在"

    def test_05_modify_success(self):
        """测试【修改渠道-成功】"""
        new_name = test_app_name + "_update"
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "app_id": test_app_id,
                "name": new_name,
                "status": 0
            }
        )
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"

    def test_06_modify_appid_empty(self):
        """测试【修改渠道-appid为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "app_id": "",
                "name": "test",
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "渠道ID不能为空"

    def test_07_modify_appid_not_exist(self):
        """测试【修改渠道-appid不存在-失败】"""
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "app_id": str(uuid.uuid4()),
                "name": "test",
                "status": 1
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "渠道ID不存在"

    def test_08_get_by_id_success(self):
        """测试【根据ID查询-成功】"""
        res = client.get(f"{API_PREFIX}/getbyid?app_id={test_app_id}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert data["item"] is not None
        assert data["item"]["app_id"] == test_app_id

    def test_09_get_by_id_empty(self):
        """测试【根据ID查询-ID为空-失败】"""
        res = client.get(f"{API_PREFIX}/getbyid?app_id=")
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "渠道ID不能为空"

    def test_10_get_all(self):
        """测试【查询所有渠道】"""
        res = client.get(f"{API_PREFIX}/getall")
        data = res.json()
        assert data["code"] == 200
        assert isinstance(data["items"], list)

    def test_11_page_query(self):
        """测试【分页查询-正常条件】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "name": "",
                "status": 1,
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

    def test_12_page_param_empty(self):
        """测试【分页参数为空校验】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "page": 0,
                "page_size": 0
            }
        )
        data = res.json()
        assert data["code"] == 204

    def test_13_is_exist_true(self):
        """测试【字段存在校验-存在】"""
        res = client.get(f"{API_PREFIX}/is_exist?field=name&value={test_app_name}_update")
        data = res.json()
        assert data["code"] == 200
        assert data["is_exist"] is True

    def test_14_is_exist_false(self):
        """测试【字段存在校验-不存在】"""
        res = client.get(f"{API_PREFIX}/is_exist?field=name&value={str(uuid.uuid4())}")
        data = res.json()
        assert data["code"] == 200
        assert data["is_exist"] is False

    def test_15_logic_delete(self):
        """测试【逻辑删除-成功】"""
        res = client.get(f"{API_PREFIX}/delete/logic?app_id={test_app_id}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "逻辑删除成功"

    def test_16_logic_delete_not_exist(self):
        """测试【逻辑删除-ID不存在】"""
        res = client.get(f"{API_PREFIX}/delete/logic?app_id={str(uuid.uuid4())}")
        data = res.json()
        assert data["code"] == 204

    def test_17_physical_delete(self):
        """测试【物理删除-成功】"""
        res = client.get(f"{API_PREFIX}/delete/physical?app_id={test_app_id}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "物理删除成功"

    def test_18_physical_delete_empty(self):
        """测试【物理删除-ID为空】"""
        res = client.get(f"{API_PREFIX}/delete/physical?app_id=")
        data = res.json()
        assert data["code"] == 204
