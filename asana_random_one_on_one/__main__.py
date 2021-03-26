import asana_random_one_on_one as oneonone
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Random one on one script. Will generate random one on ones in a given project or all projects created from template"
    )
    parser.add_argument(
        "--pat",
        type=str,
        required=True,
        help="Personal access token needed for creating the random one on ones tasks",
    )
    parser.add_argument(
        "--workspace-gid",
        type=str,
        required=True,
        help="Run the script for a given workspace",
    )
    parser.add_argument(
        "--project-gid",
        type=str,
        help="The id of a particular random 1:1 project. This will only run the script on that project",
    )
    parser.add_argument(
        "--user-gid",
        type=str,
        help="User gid used to find incompleted tasks assigned to this user. The script runs in all projects with tasks named <task-name> and are assigned to the this user",
    )
    parser.add_argument("--task-name", type=str, help="See user-gid help")
    parser.add_argument(
        "--error-project-gid",
        type=str,
        help="Accumulate errors encountered while running the script and create a task in a given project with a error report",
    )
    parser.add_argument("--debug", action="store_true", help="Runs in debug mode")
    parser.add_argument(
        "--use-name-as-id",
        action="store_true",
        help="This will use the names of the Member tasks for id instead of the id of the assignee, useful when developing as will allow multiple tasks to have the same assignee",
    )

    args = parser.parse_args()
    print(args)
    oneonone.main(
        args.pat,
        args.workspace_gid,
        user_gid=args.user_gid,
        task_name=args.task_name,
        project_gid=args.project,
        error_project_gid=args.error_project_gid,
        debug=args.debug,
        use_name_as_id=args.use_name_as_id,
    )
