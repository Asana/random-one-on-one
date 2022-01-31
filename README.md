# Asana Random one on one
A coffee walk / sit down with someone helps with shaking things up and helps co-workers getting to know each other.
You can create an Asana project for your team / office / department or any internal grouping of your choice and start having random one on ones within that group.

## Quick start
This tutorial shows how to run random one on one for a single project. If you want the script to run for multiple projects see [Advanced setup: Run for multiple projects](#advanced-setup:-run-for-multiple-projects)

### Installation
`pip3 install asana-random-one-on-one`

### Create an Asana project for the random one on ones
You will need to create an Asana project

The project will be used to schedule and store upcoming random one on one meetings for participating members.

Make sure that you have created an Asana project with 2 sections named **Members** and **Upcoming**

For each member wishing to participate, add a task to the **Member** section and assign to a participating member.

Copy the project gid from your browsers url `https://app.asana.com/0/<project_gid>/<task_gid>` for the next steps.

### Create a personal access token for your Asana
Create a [Personal Access Token](https://developers.asana.com/docs/personal-access-token) in Asana. At Asana, we created a [Guest Account](https://asana.com/guide/help/organizations/guests) to run the random one on one script, so no engineer's personal access token is used, and it's clear that there's a specific "Random one on one bot" user who is making the task updates.

Copy this Personal Access Token for the next steps.

### Find your workspace gid
You can find your workspace gids via a logged-in browser by going to https://app.asana.com/api/1.0/users/me/workspaces, or you can hit that endpoint using your PAT.

Copy the gid for the workspace your project is in for the next steps.

### Run the script
We recommend running the script once a week.

You should now have your [project_gid](#create-an-asana-project-for-the-random-one-on-ones), [personal_access_token](#create-a-personal-access-token-for-your-asana) and [workspace_gid](#find-your-workspace-gid). **NOTE**: all gids are in the form of strings, not numbers
``` python
import asana_random_one_on_one
asana_random_one_on_one.main(personal_access_token, workspace_gid, project_gid=<your_project_gid>)
```
Enjoy your random one on one

### Optional custom fields
#### Frequency
The script will schedule one on one for each member every week by default.
By adding a custom field named "Frequency" with the following options:
- Every week
- Every 2 weeks
- Every 3 weeks
- Every 4 weeks
- Never

the script can skip some members based on their frequency preference.

#### Team preference
Member can select what team they are on and if they want to be matched only with any member, other members on the same team or only members on other teams.

Have a custom fields named "**Team**" and "**Match Preferences**". Team should be a text field that can have any arbitrary string while "Match Preferences" should have:
- No preference (default)
- Only match with same team
- Only match with other teams

The script will match people based on their preference if possible.

## Advanced setup: Run for multiple projects
### Setup
**We recommend saving a project as a template, so that other groups can create their own Random one on one project easily.**

All random one on one projects should have:
- 2 sections named **Members** and **Upcoming**
- A task assigned to the same user. The task name should be the same for all projects as the script finds all tasks with a given name assigned to this user

The script will discover all the random one on one projects by finding tasks with the given name, assigned to this user.
We recommend that the personal access token be created for the same user as will be assigned to the discovery tasks.

For each member wishing to participate, add a task to the **Member** section and assign to a participating member.

### Run the script
We recommend running the script once a week

To find the user_gid of the user, log in as the user and go to https://app.asana.com/api/1.0/users/me
``` python
import asana_random_one_on_one
asana_random_one_on_one.main(personal_access_token, workspace_gid, user_gid=<user_gid>, task_name=<task_name>)
```
Enjoy your random one on one

## Run on command line
`git clone https://github.com/Asana/random-one-on-one.git`

Then go through [Installation requirements](#installation-requirements)

`python3 -m asana_random_one_on_one --pat=<personal_access_token> --workspace-gid=<workspace_gid> --project-gid=<project_gid>`

or for multiple projects

`python3 -m asana_random_one_on_one --pat=<personal_access_token> --workspace-gid=<workspace_gid> --user-gid=<user_gid> --task-name=<task_name>`


For further options run `python3 -m asana_random_one_on_one --help`
```
usage: __main__.py [-h] --pat PAT --workspace-gid WORKSPACE_GID
                   [--project-gid PROJECT_GID] [--user-gid USER_GID]
                   [--task-name TASK_NAME]
                   [--error-project-gid ERROR_PROJECT_GID] [--debug]
                   [--use-name-as-id]

Random one on one script. Will generate random one on ones in a given project
or all projects created from template

optional arguments:
  -h, --help            show this help message and exit
  --pat PAT             Personal access token needed for creating the random
                        one on ones tasks
  --workspace-gid WORKSPACE_GID
                        Run the script for a given workspace
  --project-gid PROJECT_GID
                        The id of a particular random 1:1 project. This will
                        only run the script on that project
  --user-gid USER_GID   User gid used to find incompleted tasks assigned to
                        this user. The script runs in all projects with tasks
                        named <task-name> and are assigned to the this user
  --task-name TASK_NAME
                        See user-gid help
  --error-project-gid ERROR_PROJECT_GID
                        Accumulate errors encountered while running the script
                        and create a task in a given project with a error
                        report
  --debug               Runs in debug mode
  --use-name-as-id      This will use the names of the Member tasks for id
                        instead of the id of the assignee, useful when
                        developing as will allow multiple tasks to have the
                        same assignee
```




## Contributing to the project
### Installation requirements

We recommend setting up a virtual environment to install and run your python environment. By doing so, you can eliminate
the risk that Asana Random one on one python dependencies and settings will be mixed up with any such dependencies and settings that you
may be using in other projects.

* run `python3 -m venv venv` to create a virtual environment
* run `. venv/bin/activate` to activate and enter your virtual environment
* run `pip3 install -r requirements.txt -r requirements-dev.txt`

See [these instructions](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) for further help in
setting up a virtual environment for Python