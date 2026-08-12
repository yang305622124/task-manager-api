# from user.controllers.t_user_apps_controller import router as t_user_apps_router
from task_manager_api.controllers.task_controller import router as task_router

def init_routes(app):
    # 注册路由
    app.include_router(task_router)
