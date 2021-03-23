from oneonone import bot
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Random one on one script. Will generate random one on ones in all projects created from template"
    )
    parser.add_argument(
        "--pat",
        type=str,
        required=True,
        help="Personal access token needed for creating the random one on ones tasks",
    )
    parser.add_argument("--workspace-gid", type=str, required=True, help="XCXC")
    parser.add_argument(
        "--user-gid",
        type=str,
        required=True,
        help="User gid used to find incompleted tasks assigned to this user. Runs the script in all projects for tasks named --task-name",
    )

    parser.add_argument("--task-name", type=str, help="XCXC")

    parser.add_argument("--error-project-gid", type=str, help="XCXC")

    parser.add_argument(
        "--project",
        type=str,
        help="The id of a particular random 1:1 project. This will only run the script on that project",
    )
    parser.add_argument("--debug", action="store_true", help="Runs in debug mode")
    parser.add_argument(
        "--use-name-as-id",
        action="store_true",
        help="This will use the names of the Member tasks for id's instead of the id's of the assignee, useful when developing as will allow multiple tasks to have the same assignee",
    )
    args = parser.parse_args()
    print(args)
    bot.main(
        args.pat,
        args.workspace_gid,
        args.user_gid,
        task_name=args.task_name,
        project_gid=args.project,
        error_project_gid=args.error_project_gid,
        debug=args.debug,
        use_name_as_id=args.use_name_as_id,
    )
