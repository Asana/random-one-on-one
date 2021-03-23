#!/usr/bin/env python3

from __future__ import print_function
import random
import argparse
import json
from datetime import datetime, timedelta
import asana

from construct_matches import ConstructMatches

WORK_SPACE_GID = None
MANAGE_ONE_ON_ONE_PROJECT_EXPECTED_TASK_NAME = (
    "Hi there! I am the Random one on one bot :)"
)
ERROR_PROJECT_GID = None

# Debug stuff
DEBUG = False
USE_NAME_AS_ID = False

now = datetime.now()
WEEK_NUMBER = now.isocalendar()[1]
TODAY_STR = now.strftime("%Y-%m-%d")
# Add enough days to today to get next upcoming Friday. If running script on a Friday
# this becomes the next upcoming Friday as well.
NEXT_FRIDAY = now + timedelta((3 - now.weekday()) % 7 + 1)
NEXT_FRIDAY_STR = NEXT_FRIDAY.strftime("%Y-%m-%d")


def debug_print(*args):
    if DEBUG:
        print(args)


def member_id(m):
    return member_name(m) if USE_NAME_AS_ID else m["assignee"]["gid"]


def get_custom_field_value(member, name, default=None):
    """
    :param member: A member that has custom fields, each field has a name and a value. member = {custom_fields: [{name: X, enum_value: Y}, ...], ...}
    :param name: Name of a custom field that the member might have
    :param default: If the member does not have the custom field with the given name, or the fields value in None, we return the default value.
    :return: The value of the custom field name or the given default if the member doesn't have the field or the value is None
    """
    default_value = {"name": default}
    return next(
        (
            field["enum_value"]
            for field in member["custom_fields"]
            if field["name"] == name and field["enum_value"]
        ),
        default_value,
    )["name"]


def member_name(m):
    return m["name"].strip()


def prioritize_unmatched(members, unmatched_id):
    # Unmatched from last week gets priority
    for i, member in enumerate(members):
        if member_id(member) == unmatched_id:
            members.append(
                members.pop(i)
            )  # Put at the end of the list. Since we always pop, this member will be the first one to get a match.
            break


def filter_by_frequency(members):
    number_of_weeks = (datetime.now().date() - datetime(2019, 1, 1).date()).days // 7
    switch = {
        "Never": False,
        "Every week": True,
        "Every 2 weeks": number_of_weeks % 2 == 0,
        "Every 3 weeks": number_of_weeks % 3 == 0,
        "Every 4 weeks": number_of_weeks % 4 == 0,
    }

    def _should_participate_this_week(member):
        frequency = get_custom_field_value(member, "Frequency", "Every week")
        return switch.get(frequency, False)

    return [m for m in members if _should_participate_this_week(m)]


def get_member_and_upcoming_sections(sections):
    members_section = upcoming_section = None
    for s in sections:
        section_name = s["name"].lower()
        if section_name == "members":
            members_section = s["gid"]
        elif section_name == "upcoming":
            upcoming_section = s["gid"]

    return members_section, upcoming_section


def create_one_on_one_tasks(client, this_week_id, members_tasks, unmatched_member_task):
    def _create_one_on_one_subtask(one_on_one_id, assignee_id, name):
        client.tasks.add_subtask(
            one_on_one_id,
            {
                "name": "Schedule a meet-up with {}".format(name),
                "notes": "You have been matched for a random 1:1 with {}".format(name),
                "assignee": assignee_id,
                "start_on": TODAY_STR,
                "due_on": NEXT_FRIDAY_STR,
                "workspace": WORK_SPACE_GID,
            },
        )

    while len(members_tasks) > 1:
        member1 = members_tasks.pop().get("assignee")
        name1 = member_name(member1)

        member2 = members_tasks.pop().get("assignee")
        name2 = member_name(member2)

        one_on_one_task = client.tasks.add_subtask(
            this_week_id,
            {
                "name": "Random 1:1 for {} : {}".format(name1, name2),
                "notes": "Start by finding a suitable date for your one on one and put it on the calendar",
                "workspace": WORK_SPACE_GID,
            },
        )

        _create_one_on_one_subtask(
            one_on_one_task.get("gid"), member1.get("gid"), name2
        )
        _create_one_on_one_subtask(
            one_on_one_task.get("gid"), member2.get("gid"), name1
        )

    if unmatched_member_task:
        unmatched_member = unmatched_member_task.get("assignee")
        name = member_name(unmatched_member)
        client.tasks.add_subtask(
            this_week_id,
            {
                "name": "Random One on None {}".format(name),
                "assignee": unmatched_member.get("gid"),
                "due_on": TODAY_STR,
                "notes": "Unfortunately you did not get paired this week. \nDon't worry, you will get priority next week! :tada:",
                "workspace": WORK_SPACE_GID,
            },
        )


def user_is_away(user):
    vacation_dates = user.get("vacation_dates")
    vacation_start = vacation_dates.get("start_date")
    vacation_end = vacation_dates.get("end_date")

    if vacation_start is None:  # not away
        return False

    start_date = datetime.fromisoformat(vacation_start)
    end_date = (
        datetime.fromisoformat(vacation_end) if vacation_end is not None else None
    )

    # Only filter if a user is away for the whole week
    return start_date <= now and (end_date is None or end_date >= NEXT_FRIDAY)


def generate_random_one_on_one(client, project_gid, members_section, upcoming_section):
    debug_print("Generating random one on one for project", project_gid)
    opt_fields = [
        "assignee",
        "name",
        "completed",
        "custom_fields",
        "assignee.vacation_dates",
        "assignee.name",
    ]
    members_tasks = [
        client.tasks.find_by_id(i.get("gid"), opt_fields=opt_fields)
        for i in client.tasks.find_by_section(members_section)
    ]
    members_tasks = [
        member
        for member in members_tasks
        if member.get("assignee") is not None
        and not member.get("completed")
        and not user_is_away(member.get("assignee"))
    ]  # Filter out unassigned member tasks and completed tasks
    members_tasks = filter_by_frequency(members_tasks)

    if not len(members_tasks):
        # No members in this project.
        debug_print("No members in project", members_tasks)
        return

    random.shuffle(members_tasks)

    this_weeks_name = "[{}] weeks Random 1:1".format(WEEK_NUMBER)

    # Get last week data if it exists, used for bookkeeping of a few things:
    #  - see if we have already scheduled '1 on 1's for this week (allows safe reruns)
    #  - ensure last week unmatched gets prioritized
    #  - ensure that same matches don't happen
    last_run = next(client.tasks.find_by_section(upcoming_section), None)
    last_run = client.tasks.find_by_id(last_run.get("gid")) if last_run else None

    if last_run and last_run["name"] == this_weeks_name:
        debug_print("1on1s have been scheduled for this week", last_run.get("gid"))
        return

    last_run_matches = {}
    if last_run and last_run.get("external"):
        last_run_matches = json.loads(last_run["external"]["data"])

    if last_run_matches.get("unmatched"):
        prioritize_unmatched(members_tasks, last_run_matches["unmatched"])

    debug_print("Creating matches for: ", [m["name"] for m in members_tasks])
    matches = ConstructMatches(
        members_tasks, last_run_matches, member_id, get_custom_field_value
    )
    matches.construct_matches()
    debug_print([m["name"] for m in matches.matched_members])
    debug_print("Last run matches: {}".format(last_run_matches))
    debug_print("This run matches: {}".format(matches.match_data))

    this_week = client.tasks.create_in_workspace(
        WORK_SPACE_GID,
        {
            "name": this_weeks_name,
            "notes": "Check your :one: on :one: from below",
            # "projects": [project_gid],  # python-asana version 0.9.x
            "external": {"data": json.dumps(matches.match_data)},
        },
    )
    # python-asana version 0.9.x
    # client.sections.add_task(upcoming_section, {"task": this_week.get("gid")})
    params = {"project": project_gid}
    location = (
        {"insert_before": last_run.get("gid")}
        if last_run
        else {"section": upcoming_section}
    )
    params.update(location)
    client.tasks.add_project(this_week.get("gid"), params=params)

    # Create the tasks
    create_one_on_one_tasks(
        client, this_week.get("gid"), matches.matched_members, matches.unmatched_member
    )


def run_for_a_single_project(client, project_id):
    sections = [s for s in client.sections.find_by_project(project_id)]
    members_section, upcoming_section = get_member_and_upcoming_sections(sections)
    if members_section and upcoming_section:
        generate_random_one_on_one(
            client, project_id, members_section, upcoming_section
        )
    else:
        raise Exception("Missing required sections 'Members' and 'Upcoming'")


def run_for_all_projects(client, user_gid):
    # python-asana version 0.9.x allows us to use user task list instead of user gid

    # errors will get created as tasks in the "Random one on one Bot (1:1 Feedback)" project
    errors = {}

    # Find all the tasks assigned to the random 1:1 bot across all projects
    tasks = client.tasks.find_all(
        params={
            "assignee": user_gid,
            "workspace": WORK_SPACE_GID,
            "completed_since": "now",
        }
    )
    projects_finished = {}
    error_msg = ":anguished: Could not create this weeks one on one! Reason:\n{}."

    def report_error_to_task(gid, msg):
        error = error_msg.format(msg)
        debug_print(gid, error)
        client.tasks.add_comment(gid, {"text": error})
        errors[gid] = error

    for task in tasks:
        # Make sure that bot should be managing 1:1 tasks in this project. Safeguarded by a named
        # task assigned to the bot.
        if task["name"] == MANAGE_ONE_ON_ONE_PROJECT_EXPECTED_TASK_NAME:
            task_detailed = client.tasks.find_by_id(task["gid"])
            if len(task_detailed["projects"]) > 1:
                report_error_to_task(
                    task["gid"],
                    "Task lives in more than 1 project.\n"
                    "If someone completes this task it would stop one on ones from happening in all those projects.\n"
                    "Please, only have one task assigned to me per project",
                )
            elif len(task_detailed["projects"]) == 0:
                report_error_to_task(
                    task["gid"], "Task doesn't live inside a project :mag:"
                )
            else:
                project_gid = task_detailed["projects"].pop()["gid"]
                if projects_finished.get(project_gid):
                    report_error_to_task(
                        task["gid"],
                        "Already generated this weeks one on one for this project, do I have 2 tasks in this project? :thinking_face:",
                    )
                    continue
                sections = [s for s in client.sections.find_by_project(project_gid)]
                members_section, upcoming_section = get_member_and_upcoming_sections(
                    sections
                )
                if members_section and upcoming_section:
                    generate_random_one_on_one(
                        client, project_gid, members_section, upcoming_section
                    )
                    projects_finished[project_gid] = True
                else:
                    report_error_to_task(
                        task["gid"],
                        "Missing required sections 'Members' and 'Upcoming'",
                    )
    if len(errors):
        report_errors(client, errors)


def report_errors(client, errors):
    if not ERROR_PROJECT_GID:
        return

    error_list = ""
    for gid, err in errors.items():
        error_list += f'\n <li><a data-asana-gid="{gid}" /> - {err}</li>'
    client.tasks.create_in_workspace(
        WORK_SPACE_GID,
        {
            "name": f"Errors creating random one on ones in week [{WEEK_NUMBER}]",
            "html_notes": f"<body><em>Encountered error in these 1:1 projects:</em> <ul>{error_list}</ul></body>",
            "projects": [ERROR_PROJECT_GID],
        },
    )


def main(pat, user_gid, project_gid):
    asana_client = asana.Client.access_token(pat)
    if project_gid:
        run_for_a_single_project(asana_client, project_gid)
    else:
        run_for_all_projects(asana_client, user_gid)


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
    WORK_SPACE_GID = args.workspace_gid

    if args.task_name:
        MANAGE_ONE_ON_ONE_PROJECT_EXPECTED_TASK_NAME = args.task_name
    if args.error_project_gid:
        ERROR_PROJECT_GID = args.error_project_gid

    USE_NAME_AS_ID = args.use_name_as_id
    DEBUG = args.debug
    main(args.pat, args.user_gid, args.project)
