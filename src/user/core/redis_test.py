import time
import random
import threading
from rediscluster import RedisCluster

# ===================== 配置区 =====================
# Redis 集群节点 7001-7006
STARTUP_NODES = [
    {"host": "10.211.55.30", "port": 7001},
    {"host": "10.211.55.30", "port": 7002},
    {"host": "10.211.55.30", "port": 7003},
    {"host": "10.211.55.30", "port": 7004},
    {"host": "10.211.55.30", "port": 7005},
    {"host": "10.211.55.30", "port": 7006},
]

# 压测配置
THREAD_NUM = 10        # 并发线程数
WRITE_INTERVAL = 0.01  # 单线程读写间隔(秒)
KEY_PREFIX = "prod_test:"
KEY_COUNT_RANGE = (1, 100000)  # 随机key范围
VALUE_CONTENT = "x" * 256      # value 大小 256字节，模拟业务数据
EXPIRE_SEC = 3600              # key 过期时间

# 初始化 Redis 集群客户端
rc = RedisCluster(
    startup_nodes=STARTUP_NODES,
    decode_responses=True,
    skip_full_coverage_check=True,  # 内网集群建议开启，加快连接
    socket_timeout=5
)

# 全局运行标记
RUN_FLAG = True


def worker_rw():
    """单线程：循环 写 -> 读 模拟生产流量"""
    global RUN_FLAG
    while RUN_FLAG:
        try:
            # 1. 随机生成 key
            key_suffix = random.randint(*KEY_COUNT_RANGE)
            key = f"{KEY_PREFIX}{key_suffix}"

            # 2. 写入数据
            rc.setex(key, EXPIRE_SEC, VALUE_CONTENT)

            # 3. 读取数据
            val = rc.get(key)

            time.sleep(WRITE_INTERVAL)

        except Exception as e:
            print(f"读写异常: {e}")
            time.sleep(1)


def main():
    global RUN_FLAG
    print("=== Redis 集群压测启动 ===")
    print(f"集群节点: 10.211.55.30:7001~7006")
    print(f"并发线程: {THREAD_NUM}")
    print("按 Ctrl+C 停止压测\n")

    # 启动多线程
    threads = []
    for _ in range(THREAD_NUM):
        t = threading.Thread(target=worker_rw, daemon=True)
        t.start()
        threads.append(t)

    # 主线程阻塞，捕获 Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n接收到停止信号，正在退出...")
        RUN_FLAG = False
        # 等待子线程结束
        for t in threads:
            t.join()
        print("压测已停止")


if __name__ == "__main__":
    main()