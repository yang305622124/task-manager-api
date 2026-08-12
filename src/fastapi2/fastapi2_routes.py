# from user.controllers.controllers_init import init_routes as user_init_routes
from task_manager_api.controllers.controllers_init import init_routes as task_init_tables


def init_routes(app):
    # 注册路由
    task_init_tables(app)