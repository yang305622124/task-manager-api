from rediscluster import RedisCluster

# 1. 配置集群节点
STARTUP_NODES = [
    {"host": "10.211.55.30", "port": 7001},
    {"host": "10.211.55.30", "port": 7002},
    {"host": "10.211.55.30", "port": 7003},
    {"host": "10.211.55.30", "port": 7004},
    {"host": "10.211.55.30", "port": 7005},
    {"host": "10.211.55.30", "port": 7006},
]

# 2. 连接集群
rc = RedisCluster(
    startup_nodes=STARTUP_NODES,
    decode_responses=False,  # 二进制数据不自动解码
    skip_full_coverage_check=True  # 内网集群建议开启，加快连接
)

def create_string_bigkey():
    # 构造不同大小的内容
    size_10kb  = "x" * 10 * 1024    # 10KB 临界大Key
    size_100kb = "x" * 100 * 1024   # 100KB 严重大Key
    size_1mb   = "x" * 1024 * 1024  # 1MB 高危大Key

    # 写入集群
    rc.set("bigkey:string:10kb",  size_10kb)
    rc.set("bigkey:string:100kb", size_100kb)
    rc.set("bigkey:string:1mb",   size_1mb)

    print("String 大Key 注入完成：")
    print("bigkey:string:10kb  -> 10KB")
    print("bigkey:string:100kb -> 100KB")
    print("bigkey:string:1mb   -> 1MB")

if __name__ == "__main__":
    create_string_bigkey()