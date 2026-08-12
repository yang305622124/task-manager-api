
import uuid
from fastapi.testclient import TestClient
from main import app  # 请根据自己项目入口调整

# 挂载测试客户端
client = TestClient(app)

# 统一接口前缀
API_PREFIX = "/api/v1/task"

# 全局测试变量
test_task_title = f"test_{str(uuid.uuid4())[:8]}"
test_task_id = ""


class TestTaskController:
    """任务表 task 单元测试（全覆盖所有接口分支）"""

    # ====================== create 新增任务 ======================

    def test_01_create_success(self):
        """测试【新增任务-成功场景】"""
        global test_task_id
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "title": test_task_title,
                "description": "测试任务描述",
                "status": "todo"
            }
        )
        data = res.json()
        assert res.status_code == 200
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert data["task_id"] != ""
        assert data["request_id"] != ""
        test_task_id = data["task_id"]

    def test_02_create_title_empty(self):
        """测试【新增任务-title为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "title": "",
                "description": "测试",
                "status": "todo"
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "任务标题不能为空"

    def test_03_create_title_exist(self):
        """测试【新增任务-标题重复-失败】"""
        res = client.post(
            f"{API_PREFIX}/create",
            json={
                "title": test_task_title,
                "description": "重复标题测试",
                "status": "todo"
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "任务标题已存在"

    # ====================== modify 修改任务 ======================

    def test_04_modify_success(self):
        """测试【修改任务-成功】"""
        new_title = test_task_title + "_update"
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "id": test_task_id,
                "title": new_title,
                "description": "修改后的描述",
                "status": "in_progress"
            }
        )
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"

    def test_05_modify_id_empty(self):
        """测试【修改任务-id为空-失败】"""
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "id": "",
                "title": "test",
                "status": "todo"
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "任务ID不能为空"

    def test_06_modify_id_not_exist(self):
        """测试【修改任务-id不存在-失败】"""
        res = client.post(
            f"{API_PREFIX}/modify",
            json={
                "id": str(uuid.uuid4()),
                "title": "test",
                "status": "todo"
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "任务ID不存在"

    # ====================== getbyid 单条查询 ======================

    def test_07_get_by_id_success(self):
        """测试【根据ID查询任务-成功】"""
        res = client.get(f"{API_PREFIX}/getbyid?id={test_task_id}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert data["item"] is not None
        assert data["item"]["id"] == test_task_id
        assert data["item"]["title"] == test_task_title + "_update"
        assert data["item"]["status"] == "in_progress"

    def test_08_get_by_id_empty(self):
        """测试【根据ID查询-id为空-失败】"""
        res = client.get(f"{API_PREFIX}/getbyid?id=")
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "任务ID不能为空"

    def test_09_get_by_id_not_exist(self):
        """测试【根据ID查询-id不存在-失败】"""
        res = client.get(f"{API_PREFIX}/getbyid?id={str(uuid.uuid4())}")
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "数据不存在"

    # ====================== getall 查询全部 ======================

    def test_10_get_all(self):
        """测试【查询所有任务】"""
        res = client.get(f"{API_PREFIX}/getall")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0

    # ====================== get4page 分页查询 ======================

    def test_11_page_query_all(self):
        """测试【分页查询-无条件-正常】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "page": 1,
                "page_size": 10
            }
        )
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert "total" in data
        assert "items" in data
        assert data["total"] > 0

    def test_12_page_query_with_title(self):
        """测试【分页查询-按标题模糊查询】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "title": test_task_title[:6],
                "page": 1,
                "page_size": 10
            }
        )
        data = res.json()
        assert data["code"] == 200
        assert data["total"] >= 1

    def test_13_page_query_with_status(self):
        """测试【分页查询-按状态查询】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "status": "in_progress",
                "page": 1,
                "page_size": 10
            }
        )
        data = res.json()
        assert data["code"] == 200
        assert data["total"] >= 1

    def test_14_page_query_with_time_range(self):
        """测试【分页查询-按时间范围查询】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "begin_time": "2020-01-01 00:00:00",
                "end_time": "2099-12-31 23:59:59",
                "page": 1,
                "page_size": 10
            }
        )
        data = res.json()
        assert data["code"] == 200
        assert data["total"] >= 1

    def test_15_page_param_empty(self):
        """测试【分页参数为空校验-失败】"""
        res = client.post(
            f"{API_PREFIX}/get4page",
            json={
                "page": 0,
                "page_size": 0
            }
        )
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "页码/分页条数不能为空"

    # ====================== is_exist 唯一性校验 ======================

    def test_16_is_exist_true(self):
        """测试【字段存在校验-存在】"""
        res = client.get(f"{API_PREFIX}/is_exist?field=title&value={test_task_title}_update")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert data["is_exist"] is True

    def test_17_is_exist_false(self):
        """测试【字段存在校验-不存在】"""
        res = client.get(f"{API_PREFIX}/is_exist?field=title&value={str(uuid.uuid4())}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "成功"
        assert data["is_exist"] is False

    # ====================== delete_physical 物理删除 ======================

    def test_18_physical_delete_not_exist(self):
        """测试【物理删除-ID不存在-失败】"""
        res = client.get(f"{API_PREFIX}/delete/physical?id={str(uuid.uuid4())}")
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "任务ID不存在"

    def test_19_physical_delete_empty(self):
        """测试【物理删除-id为空-失败】"""
        res = client.get(f"{API_PREFIX}/delete/physical?id=")
        data = res.json()
        assert data["code"] == 204
        assert data["msg"] == "任务ID不能为空"

    def test_20_physical_delete_success(self):
        """测试【物理删除-成功】（最后执行，清理测试数据）"""
        res = client.get(f"{API_PREFIX}/delete/physical?id={test_task_id}")
        data = res.json()
        assert data["code"] == 200
        assert data["msg"] == "物理删除成功"
