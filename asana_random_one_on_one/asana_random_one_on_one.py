#!/usr/bin/env python3
from __future__ import print_function
import random
import argparse
import json
from datetime import datetime, timedelta
import asana

from asana_random_one_on_one.config import Config
from asana_random_one_on_one.construct_matches import ConstructMatches


def next_friday():
    # Add enough days to today to get next upcoming Friday. If running script on a Friday
    # this becomes the next upcoming Friday as well.
    now = datetime.now()
    return now + timedelta((3 - now.weekday()) % 7 + 1)


def debug_print(config, *args):
    if config.debug:
        print(args)


def member_id(config):
    def inner(m):
        return member_name(m) if config.use_name_as_id else m["assignee"]["gid"]

    return inner


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


def prioritize_unmatched(config, members, unmatched_id):
    # Unmatched from last week gets priority
    for i, member in enumerate(members):
        if member_id(config)(member) == unmatched_id:
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


def create_one_on_one_tasks(config, this_week_id, members_tasks, unmatched_member_task):
    today_str = datetime.now().strftime("%Y-%m-%d")
    next_friday_str = next_friday().strftime("%Y-%m-%d")

    def _create_one_on_one_subtask(one_on_one_id, assignee_id, name):
        config.client.tasks.add_subtask(
            one_on_one_id,
            {
                "name": "Schedule a meet-up with {}".format(name),
                "notes": "You have been matched for a random 1:1 with {}".format(name),
                "assignee": assignee_id,
                "start_on": today_str,
                "due_on": next_friday_str,
                "workspace": config.work_space_gid,
            },
        )

    while len(members_tasks) > 1:
        member1 = members_tasks.pop().get("assignee")
        name1 = member_name(member1)

        member2 = members_tasks.pop().get("assignee")
        name2 = member_name(member2)

        one_on_one_task = config.client.tasks.add_subtask(
            this_week_id,
            {
                "name": "Random 1:1 for {} : {}".format(name1, name2),
                "notes": "Start by finding a suitable date for your one on one and put it on the calendar",
                "workspace": config.work_space_gid,
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
        config.client.tasks.add_subtask(
            this_week_id,
            {
                "name": "Random One on None {}".format(name),
                "assignee": unmatched_member.get("gid"),
                "due_on": today_str,
                "notes": "Unfortunately you did not get paired this week. \nDon't worry, you will get priority next week! :tada:",
                "workspace": config.work_space_gid,
            },
        )


def user_is_away(user):
    now = datetime.now()
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
    return start_date <= now and (end_date is None or end_date >= next_friday())


def generate_random_one_on_one(config, project_gid, members_section, upcoming_section):
    debug_print(config, "Generating random one on one for project", project_gid)
    opt_fields = [
        "assignee",
        "name",
        "completed",
        "custom_fields",
        "assignee.vacation_dates",
        "assignee.name",
    ]
    members_tasks = [
        config.client.tasks.find_by_id(i.get("gid"), opt_fields=opt_fields)
        for i in config.client.tasks.find_by_section(members_section)
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
        debug_print(config, "No members in project", members_tasks)
        return

    random.shuffle(members_tasks)

    this_weeks_name = "[{}] weeks Random 1:1".format(config.week_number)

    # Get last week data if it exists, used for bookkeeping of a few things:
    #  - see if we have already scheduled '1 on 1's for this week (allows safe reruns)
    #  - ensure last week unmatched gets prioritized
    #  - ensure that same matches don't happen
    last_run = next(config.client.tasks.find_by_section(upcoming_section), None)
    last_run = config.client.tasks.find_by_id(last_run.get("gid")) if last_run else None

    if last_run and last_run["name"] == this_weeks_name:
        debug_print(
            config,
            "1on1s have been scheduled for this week already",
            last_run.get("gid"),
        )
        return

    last_run_matches = {}
    if last_run and last_run.get("external"):
        last_run_matches = json.loads(last_run["external"]["data"])

    if last_run_matches.get("unmatched"):
        prioritize_unmatched(config, members_tasks, last_run_matches["unmatched"])

    debug_print(config, "Creating matches for: ", [m["name"] for m in members_tasks])
    matches = ConstructMatches(
        members_tasks, last_run_matches, member_id(config), get_custom_field_value
    )
    matches.construct_matches()
    debug_print(config, [m["name"] for m in matches.matched_members])
    debug_print(config, "Last run matches: {}".format(last_run_matches))
    debug_print(config, "This run matches: {}".format(matches.match_data))

    this_week = config.client.tasks.create_in_workspace(
        config.work_space_gid,
        {
            "name": this_weeks_name,
            "notes": "Check your :one: on :one: from below",
            "external": {"data": json.dumps(matches.match_data)},
        },
    )
    params = {"project": project_gid}
    location = (
        {"insert_before": last_run.get("gid")}
        if last_run
        else {"section": upcoming_section}
    )
    params.update(location)
    config.client.tasks.add_project(this_week.get("gid"), params=params)

    # Create the tasks
    create_one_on_one_tasks(
        config, this_week.get("gid"), matches.matched_members, matches.unmatched_member
    )


def run_for_a_single_project(config, project_id):
    sections = [s for s in config.client.sections.find_by_project(project_id)]
    members_section, upcoming_section = get_member_and_upcoming_sections(sections)
    if members_section and upcoming_section:
        generate_random_one_on_one(
            config, project_id, members_section, upcoming_section
        )
    else:
        raise Exception("Missing required sections 'Members' and 'Upcoming'")


def run_for_all_projects(config):
    # errors will get created as tasks in the "Random one on one Bot (1:1 Feedback)" project
    errors = {}

    # Find all the tasks assigned to the random 1:1 bot across all projects
    tasks = config.client.tasks.find_all(
        params={
            "assignee": config.user_gid,
            "workspace": config.work_space_gid,
            "completed_since": "now",
        }
    )
    projects_finished = {}
    error_msg = ":anguished: Could not create this weeks one on one! Reason:\n{}."

    def report_error_to_task(gid, msg):
        error = error_msg.format(msg)
        debug_print(config, gid, error)
        config.client.tasks.add_comment(gid, {"text": error})
        errors[gid] = error

    for task in tasks:
        # Make sure that bot should be managing 1:1 tasks in this project. Safeguarded by a named
        # task assigned to the bot.
        if task["name"] == config.manage_one_on_one_project_expected_task_name:
            task_detailed = config.client.tasks.find_by_id(task["gid"])
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
                sections = [
                    s for s in config.client.sections.find_by_project(project_gid)
                ]
                members_section, upcoming_section = get_member_and_upcoming_sections(
                    sections
                )
                if members_section and upcoming_section:
                    generate_random_one_on_one(
                        config, project_gid, members_section, upcoming_section
                    )
                    projects_finished[project_gid] = True
                else:
                    report_error_to_task(
                        task["gid"],
                        "Missing required sections 'Members' and 'Upcoming'",
                    )
    if len(errors):
        report_errors(config, errors)


def report_errors(config, errors):
    if not config.error_project_gid:
        return

    error_list = ""
    for gid, err in errors.items():
        error_list += f'\n <li><a data-asana-gid="{gid}" /> - {err}</li>'
    config.client.tasks.create_in_workspace(
        config.work_space_gid,
        {
            "name": f"Errors creating random one on ones in week [{config.week_number}]",
            "html_notes": f"<body><em>Encountered error in these 1:1 projects:</em> <ul>{error_list}</ul></body>",
            "projects": [config.error_project_gid],
        },
    )


def main(
    pat,
    work_space_gid,
    project_gid=None,
    task_name=None,
    user_gid=None,
    error_project_gid=None,
    debug=False,
    use_name_as_id=False,
):

    if any([user_gid, task_name]):
        if project_gid:
            raise Exception(
                "Either provide project_gid for a single project run or user_gid and task_name for a multiple project run"
            )
        if not user_gid:
            raise Exception("Missing user_gid needed to discover projects")
        if not task_name:
            raise Exception("Missing task_name needed to discover projects")

    asana_client = asana.Client.access_token(pat)
    config = Config(
        asana_client,
        work_space_gid,
        user_gid,
        task_name,
        error_project_gid,
        debug,
        use_name_as_id,
    )

    if project_gid:
        run_for_a_single_project(config, project_gid)
    else:
        run_for_all_projects(config)
