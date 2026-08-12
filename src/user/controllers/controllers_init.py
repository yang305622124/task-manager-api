from user.controllers.t_user_apps_controller import router as t_user_apps_router
from user.controllers.t_user_users_controller import router as t_user_users_router

def init_routes(app):
    # 注册路由
    app.include_router(t_user_apps_router)
    app.include_router(t_user_users_router)