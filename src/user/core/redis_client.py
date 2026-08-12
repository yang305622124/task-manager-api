
import redis
from typing import Optional

# ===================== Redis 全局配置（可根据环境自行修改）====================
# 服务地址
REDIS_HOST: str = "10.211.55.20"
# 端口
REDIS_PORT: int = 6379
# 密码，无密码填空字符串
REDIS_PASSWORD: str = "58fTm6Li*"
# 数据库索引
REDIS_DB: int = 0
# 连接超时时间
REDIS_TIMEOUT: int = 5
# 自动解码字符串（返回str，无需手动decode）
REDIS_DECODE: bool = True


class RedisClient:
    """
    Redis全局单例客户端
    适配项目DAO层缓存读写、过期设置、缓存删除场景
    兼容字符串序列化数据，完美适配用户/渠道缓存逻辑
    """
    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """获取Redis单例连接客户端"""
        if not cls._instance:
            cls._instance = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=REDIS_DECODE,
                socket_timeout=REDIS_TIMEOUT,
                retry_on_timeout=True,  # 超时自动重试
                health_check_interval=30  # 定时健康检测
            )
        return cls._instance


# 全局统一实例（项目所有地方直接导入使用）
redis_client = RedisClient.get_client()
