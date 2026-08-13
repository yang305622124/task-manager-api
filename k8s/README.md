# Kubernetes 部署配置说明

本目录包含 Task Manager API 在 Kubernetes 集群中部署所需的全部资源配置文件。

---

## 文件总览

| 文件 | 资源类型 | 作用 |
|---|---|---|
| [namespace.yaml](./namespace.yaml) | Namespace | 创建独立命名空间，隔离项目资源 |
| [configmap.yaml](./configmap.yaml) | ConfigMap | 存储非敏感环境变量配置 |
| [deployment.yaml](./deployment.yaml) | Deployment | 定义应用容器副本、资源限制、健康探针 |
| [service.yaml](./service.yaml) | Service | 集群内部服务发现与负载均衡 |
| [ingress.yaml](./ingress.yaml) | Ingress | 外部流量入口规则 |

---

## 部署顺序

```bash
# 按依赖顺序执行
kubectl apply -f namespace.yaml      # 1. 先创建命名空间
kubectl apply -f configmap.yaml      # 2. 创建配置（Deployment 依赖此配置）
kubectl apply -f deployment.yaml     # 3. 部署应用
kubectl apply -f service.yaml        # 4. 暴露服务
kubectl apply -f ingress.yaml        # 5. 配置入口

# 或一键部署全部资源
kubectl apply -f k8s/
```

---

## 各文件详细说明

### 1. namespace.yaml — 命名空间

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: task-manager
  labels:
    app: task-manager-api
```

**作用**：创建一个名为 `task-manager` 的独立命名空间，将项目所有资源（Deployment、Service、ConfigMap 等）隔离在其中，避免与其他项目资源冲突。

**常用命令**：
```bash
# 查看命名空间下所有资源
kubectl get all -n task-manager

# 仅查看 Pod
kubectl get pods -n task-manager
```

---

### 2. configmap.yaml — 环境变量配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: task-manager-api
  namespace: task-manager
data:
  PORT: "8080"
  LOG_LEVEL: "INFO"
  DB_HOST: "mysql.task-manager.svc.cluster.local"
  DB_PORT: "3306"
  DB_NAME: "task-manager-api"
  REDIS_HOST: "redis.task-manager.svc.cluster.local"
  REDIS_PORT: "6379"
```

**作用**：将非敏感配置项集中存储，Deployment 通过 `envFrom` 引用，将配置注入为容器环境变量。

**配置项说明**：

| 变量名 | 默认值 | 说明 |
|---|---|---|
| `PORT` | `8080` | 服务监听端口 |
| `LOG_LEVEL` | `INFO` | 日志级别（DEBUG / INFO / WARNING / ERROR / CRITICAL） |
| `DB_HOST` | `mysql.task-manager.svc.cluster.local` | MySQL 服务地址（K8s 内部 DNS） |
| `DB_PORT` | `3306` | MySQL 端口 |
| `DB_NAME` | `task-manager-api` | 数据库名称 |
| `REDIS_HOST` | `redis.task-manager.svc.cluster.local` | Redis 服务地址（K8s 内部 DNS） |
| `REDIS_PORT` | `6379` | Redis 端口 |

> 修改配置后需重启 Pod 生效：`kubectl rollout restart deployment/task-manager-api -n task-manager`

---

### 3. deployment.yaml — 应用部署

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 2
  containers:
    - name: task-manager-api
      image: task-manager-api:latest
      resources:
        requests:  { cpu: 100m, memory: 128Mi }
        limits:    { cpu: 200m, memory: 256Mi }
      livenessProbe:  { httpGet: /health, port: 8080 }
      readinessProbe: { httpGet: /health, port: 8080 }
```

**作用**：定义应用容器的运行规格，包括副本数、镜像、资源限制和健康检查。

**关键配置说明**：

| 配置项 | 值 | 说明 |
|---|---|---|
| `replicas` | 2 | 运行 2 个 Pod 副本，保证高可用 |
| `image` | `task-manager-api:latest` | 容器镜像（Jenkins 会自动替换为实际构建版本） |
| `imagePullPolicy` | `IfNotPresent` | 本地不存在时才拉取 |
| `containerPort` | 8080 | 容器监听端口 |
| `envFrom.configMapRef` | `task-manager-api` | 从 ConfigMap 注入全部环境变量 |

**资源限制**：

| 类型 | CPU | 内存 |
|---|---|---|
| `requests`（最低保障） | 100m（0.1 核） | 128Mi |
| `limits`（最高上限） | 200m（0.2 核） | 256Mi |

**健康探针**：

| 探针 | 检测方式 | 启动延迟 | 检测间隔 | 超时时间 | 失败阈值 |
|---|---|---|---|---|---|
| **livenessProbe**（存活） | HTTP GET `/health` | 15s | 20s | 5s | 3 次 |
| **readinessProbe**（就绪） | HTTP GET `/health` | 10s | 10s | 5s | 3 次 |

- **livenessProbe**：连续 3 次失败后重启容器，防止死锁
- **readinessProbe**：连续 3 次失败后从 Service 摘除 Pod，停止接收流量

---

### 4. service.yaml — 服务暴露

```yaml
apiVersion: v1
kind: Service
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: 8080
      protocol: TCP
  selector:
    app: task-manager-api
```

**作用**：为 Deployment 的 Pod 提供稳定的集群内部访问入口，通过标签选择器自动发现并负载均衡到所有匹配 Pod。

**配置说明**：

| 配置项 | 值 | 说明 |
|---|---|---|
| `type` | `ClusterIP` | 仅集群内部可访问，不暴露到外部 |
| `port` | 8080 | Service 对外端口 |
| `targetPort` | 8080 | 转发到 Pod 的端口 |
| `selector` | `app: task-manager-api` | 匹配 Deployment 的 Pod 标签 |

**集群内部访问方式**：
```bash
# 同命名空间内其他 Pod 可通过以下地址访问
http://task-manager-api.task-manager:8080

# 跨命名空间访问
http://task-manager-api.task-manager.svc.cluster.local:8080
```

---

### 5. ingress.yaml — 外部入口

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  rules:
    - http:
        paths:
          - path: /task-manager(/|$)(.*)
            backend:
              service:
                name: task-manager-api
                port:
                  number: 8080
```

**作用**：配置 Nginx Ingress Controller 的路由规则，将外部请求 `/task-manager/*` 转发到集群内部 Service。

**配置说明**：

| 配置项 | 值 | 说明 |
|---|---|---|
| `ingress.class` | `nginx` | 使用 Nginx Ingress Controller |
| `path` | `/task-manager(/|$)(.*)` | 匹配 `/task-manager` 前缀的所有请求 |
| `rewrite-target` | `/$2` | 去除 `/task-manager` 前缀后转发（如 `/task-manager/health` → `/health`） |
| `proxy-body-size` | `500m` | 允许最大请求体 500MB |
| `pathType` | `ImplementationSpecific` | 路径匹配由 Ingress Controller 实现决定 |

**外部访问方式**：
```bash
# 通过 Ingress 访问（需配置 hosts 或 DNS）
http://<ingress-host>/task-manager/health
http://<ingress-host>/task-manager/tasks
```

---

## 资源关系图

```
外部请求
    │
    ▼
┌─────────────┐
│   Ingress   │  /task-manager/* → rewrite → /*
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│   Service   │────▶│  Pod (副本1)  │
│  ClusterIP  │     └──────────────┘
│   :8080     │     ┌──────────────┐
│             │────▶│  Pod (副本2)  │
└─────────────┘     └──────────────┘
       ▲                   │
       │            ┌──────┴──────┐
       │            │  ConfigMap  │
       └────────────│  (环境变量)  │
                    └─────────────┘
```

---

## 常用运维命令

```bash
# 查看部署状态
kubectl get all -n task-manager

# 查看 Pod 日志
kubectl logs -f deployment/task-manager-api -n task-manager

# 手动扩容到 3 副本
kubectl scale deployment/task-manager-api --replicas=3 -n task-manager

# 滚动更新（替换镜像版本）
kubectl set image deployment/task-manager-api \
  task-manager-api=<新镜像地址> -n task-manager

# 查看滚动更新状态
kubectl rollout status deployment/task-manager-api -n task-manager

# 回滚到上一版本
kubectl rollout undo deployment/task-manager-api -n task-manager

# 重启 Pod（配置变更后）
kubectl rollout restart deployment/task-manager-api -n task-manager
```
# task-manager-api