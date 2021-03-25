# Asana Random one on one
A coffee walk / sit down with someone helps with shaking things up and helps co-workers getting to know each other.
You can create an Asana project for your team / office / department or any internal grouping of your choice and start having random one on ones within that group.

### Installation
`pip3 install asana-random-one-on-one`

### Create an Asana project for the random one on ones
You will need to create an Asana project 
The project will be used to schedule and store upcoming random one on one meetings for participating members.

Make sure that you have created an Asana project with
- At least 2 sections named **Members** and **Upcoming**
- A task assigned to a user. Name the task to something distinct as the script finds all tasks with a given name assigned to this user

For each member, add a task to the **Member** section and assign to a participating member.

**We recommend saving this project as a template, so that other groups can create their own Random one on one project easily.**

![createrandomproject](https://user-images.githubusercontent.com/9914844/112172529-b333ef00-8bec-11eb-8b99-a9d10887a61d.gif)

### Create a personal access token for your Asana
Create a [Personal Access Token](https://developers.asana.com/docs/personal-access-token) in Asana. At Asana, we created a [Guest Account](https://asana.com/guide/help/organizations/guests) to run the random one on one script, so no engineer's personal access token is used, and it's clear that there's a specific "Random one on one bot" user who is making the task updates.

We recommend that the personal access token be created for the same user as will be assigned to the discovery tasks.

Copy this Personal Access Token for the next steps.

### Run the script
Either via package
``` python
import asana_random_one_on_one
asana_random_one_on_one.main(personal_access_token, workspace_gid, user_gid, task_name)
```
Or, alternatively, you can clone the repo and run via command line

`git clone https://github.com/Asana/random-one-on-one.git`

Then go through [Installing requirements](#installing-requirements)

`python3 -m asana_random_one_on_one --pat=<personal_access_token> --workspace-gid=<workspace_gid> --user-gid=<user_id> --task-name=<task_name>`


For further options run `python3 -m asana_random_one_on_one --help`
```
usage: __main__.py [-h] --pat PAT --workspace-gid WORKSPACE_GID --user-gid
                   USER_GID --task-name TASK_NAME
                   [--error-project-gid ERROR_PROJECT_GID] [--project PROJECT]
                   [--debug] [--use-name-as-id]

Random one on one script. Will generate random one on ones in all projects
created from template

optional arguments:
  -h, --help            show this help message and exit
  --pat PAT             Personal access token needed for creating the random
                        one on ones tasks
  --workspace-gid WORKSPACE_GID
                        Run the script for a given workspace
  --user-gid USER_GID   User gid used to find incompleted tasks assigned to
                        this user. The script runs in all projects with tasks
                        named <task-name> and are assigned to the this user
  --task-name TASK_NAME
                        See user-gid help
  --error-project-gid ERROR_PROJECT_GID
                        Accumulate errors encountered while running the script
                        and create a task in a given project with a error
                        report
  --project PROJECT     The id of a particular random 1:1 project. This will
                        only run the script on that project
  --debug               Runs in debug mode
  --use-name-as-id      This will use the names of the Member tasks for id's
                        instead of the id's of the assignee, useful when
                        developing as will allow multiple tasks to have the
                        same assignee
```

Enjoy your random one on one


## Contributing to the project
### Installing requirements

We recommend setting up a virtual environment to install and run your python environment. By doing so, you can eliminate
the risk that Asana Random one on one python dependencies and settings will be mixed up with any such dependencies and settings that you
may be using in other projects.
Once you have that activated (see [Installing a Virtual Environment for Python](#installing-a-virtual-environment-for-python) below), you should install all required python dependencies using

`pip3 install -r requirements.txt -r requirements-dev.txt`

### Installing a Virtual Environment for Python

See [these instructions](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) for help in
setting up a virtual environment for Python, or use the following TL;DR version:

* run `python3 -m venv v-env` to create a virtual environment
* run `source v-env/bin/activate` to activate and enter your virtual environment
* once activated, run `deactivate` to deactivate and leave your virtual environment
