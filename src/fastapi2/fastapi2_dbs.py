from user.daos.db_init import init_tables as user_init_tables
from task_manager_api.daos.db_init import init_tables as task_init_tables


def init_dbs():
    task_init_tables()
