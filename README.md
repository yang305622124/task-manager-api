# Task Manager API

<!-- CI 状态徽章（请替换为实际仓库地址） -->
![Build](https://github.com/your-org/task-manager-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

一个基于 FastAPI 构建的任务管理 RESTful API 服务，支持任务的增删改查、分页搜索及字段唯一性校验，采用多阶段 Docker 构建，可通过 Minikube 进行容器编排部署。

---

## 项目简介

Task Manager API 提供完整的任务生命周期管理，包括：

- **任务创建**：支持标题唯一性校验
- **任务修改**：动态字段更新
- **任务删除**：物理删除
- **任务查询**：单条查询 / 全量查询 / 分页查询（支持标题模糊搜索、状态筛选、时间范围过滤）
- **字段唯一性校验**：任意字段值存在性检测

---

## 技术栈说明

| 分类 | 技术 |
|---|---|
| Web 框架 | FastAPI |
| ASGI 服务器 | Uvicorn |
| ORM | SQLAlchemy |
| 数据库 | MySQL（PyMySQL 驱动） |
| 缓存 | Redis |
| 数据校验 | Pydantic |
| 容器化 | Docker（多阶段构建） |
| 编排部署 | Kubernetes / Minikube |
| 包管理 | uv / pip |

---

## 本地开发环境搭建

### 1. 环境要求

- Python >= 3.11
- MySQL 数据库
- （可选）Redis

### 2. 克隆项目

```bash
git clone https://github.com/your-org/task-manager-api.git
cd task-manager-api
```

### 3. 创建虚拟环境

```bash
# 使用 uv（推荐）
uv venv .venv
source .venv/bin/activate

# 或使用 Python 内置 venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置数据库

修改 `src/task_manager_api/daos/db_init.py` 中的数据库连接配置：

```python
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "db": "task-manager-api"
}
```

### 6. 启动服务

```bash
cd src
python main.py
```

服务启动后访问：
- API 文档（Swagger UI）：http://127.0.0.1:8080/docs
- API 文档（ReDoc）：http://127.0.0.1:8080/redoc

---

## API 接口一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/task/create` | 新增任务 |
| POST | `/api/v1/task/modify` | 修改任务 |
| GET | `/api/v1/task/delete/physical` | 物理删除任务 |
| GET | `/api/v1/task/getbyid` | 根据 ID 查询任务 |
| GET | `/api/v1/task/getall` | 查询所有任务 |
| POST | `/api/v1/task/get4page` | 分页查询任务 |
| GET | `/api/v1/task/is_exist` | 字段唯一性校验 |

---

## Docker 构建和运行说明

### 构建镜像

采用多阶段构建（Multi-stage Build），最终镜像仅包含运行时必要文件，以非 root 用户运行。

```bash
docker build -t task-manager-api:latest .
```

### 运行容器

```bash
# 默认端口 8080
docker run -d -p 8080:8080 --name task-api task-manager-api:latest

# 自定义端口
docker run -d -p 9090:9090 -e PORT=9090 --name task-api task-manager-api:latest
```

### 验证服务

```bash
curl http://127.0.0.1:8080/api/v1/task/getall
```

---

## Minikube 部署步骤

### 1. 启动 Minikube

```bash
minikube start
```

### 2. 构建镜像到 Minikube 内部

```bash
eval $(minikube docker-env)
docker build -t task-manager-api:latest .
```

### 3. 创建命名空间

```bash
kubectl apply -f k8s/namespace.yaml
```

### 4. 部署应用

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 5. 验证部署状态

```bash
kubectl get all -n task-manager
```

### 6. 访问服务

```bash
# 方式一：端口转发
kubectl port-forward svc/task-manager-api 8080:8080 -n task-manager

# 方式二：Minikube tunnel
minikube tunnel
```

---

## 屏幕截图

### `kubectl get all -n task-manager` 输出示例

```
NAME                                     READY   STATUS    RESTARTS   AGE
pod/task-manager-api-6d8f7b6c4-x2k9n    1/1     Running   0          5m

NAME                         TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
service/task-manager-api     NodePort   10.100.23.45    <none>        8080:30080/TCP   5m

NAME                                 READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/task-manager-api     1/1     1            1           5m

NAME                                           DESIRED   CURRENT   READY   AGE
replicaset.apps/task-manager-api-6d8f7b6c4    1         1         1       5m
```

### API 调用成功响应示例

**创建任务** `POST /api/v1/task/create`

```bash
curl -X POST http://127.0.0.1:8080/api/v1/task/create \
  -H "Content-Type: application/json" \
  -d '{"title": "完成项目文档", "description": "编写 README.md", "status": "todo"}'
```

```json
{
  "code": 200,
  "msg": "成功",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

**查询任务** `GET /api/v1/task/getbyid?id=a1b2c3d4-e5f6-7890-abcd-ef1234567890`

```json
{
  "code": 200,
  "msg": "成功",
  "item": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "完成项目文档",
    "description": "编写 README.md",
    "status": "todo",
    "created_at": "2025-08-11T10:30:00",
    "updated_at": null
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**分页查询** `POST /api/v1/task/get4page`

```bash
curl -X POST http://127.0.0.1:8080/api/v1/task/get4page \
  -H "Content-Type: application/json" \
  -d '{"title": "文档", "status": "todo", "page": 1, "page_size": 10}'
```

```json
{
  "code": 200,
  "msg": "成功",
  "total": 1,
  "items": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "完成项目文档",
      "description": "编写 README.md",
      "status": "todo",
      "created_at": "2025-08-11T10:30:00",
      "updated_at": null
    }
  ],
  "request_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
}
```

---

## 项目结构

```
task-manager-api/
├── src/
│   ├── fastapi2/                  # 框架核心（路由/数据库初始化/异常处理）
│   ├── task_manager_api/
│   │   ├── controllers/           # 控制器层（接口定义）
│   │   ├── daos/                  # 数据访问层（CRUD 操作）
│   │   ├── models/                # 模型层（ORM 映射）
│   │   ├── sql/                   # SQL 建表脚本
│   │   └── tests/                 # 单元测试
│   └── main.py                    # 应用入口
├── k8s/                           # Kubernetes 部署配置
├── Dockerfile                     # 多阶段构建
├── requirements.txt               # Python 依赖
└── pyproject.toml                 # 项目元信息
```

---

## License

[MIT](LICENSE)
