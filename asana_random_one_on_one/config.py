from datetime import datetime, timedelta


class Config(object):
    def __init__(
        self,
        client,
        work_space_gid,
        user_gid,
        task_name,
        error_project_gid,
        debug,
        use_name_as_id,
    ):
        self.client = client
        self.user_gid = user_gid
        self.work_space_gid = work_space_gid
        self.manage_one_on_one_project_expected_task_name = task_name
        self.error_project_gid = error_project_gid
        self.week_number = datetime.now().isocalendar()[1]

        # Debug stuff
        self.debug = debug
        self.use_name_as_id = use_name_as_id
