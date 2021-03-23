from datetime import datetime, timedelta


class Config(object):
    def __init__(self, client, work_space_gid, user_gid):
        self.client = client
        self.user_gid = user_gid
        self.work_space_gid = work_space_gid
        self.manage_one_on_one_project_expected_task_name = (
            "Hi there! I am the Random one on one bot :)"
        )
        self.error_project_gid = None
        self.week_number = datetime.now().isocalendar()[1]

        # Debug stuff
        self.debug = False
        self.use_name_as_id = False
