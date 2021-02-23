# Asana Random one on one
A coffee walk / sit down with someone helps with shaking things up and helps co-workers getting to know each other.
You can create an Asana project for your team / office / department or any internal grouping of your choice and start having random one on ones within that group.

### Installation
We recommend setting up a virtual environment to install and run your python environment. By doing so, you can eliminate
the risk that Asana Random one on one python dependencies and settings will be mixed up with any such dependencies and settings that you
may be using in other projects. Once you have that activated (see [Installing a Virtual Environment for Python](#installing-a-virtual-environment-for-python) below), you should install all required python dependencies using

`pip3 install -r requirements.txt`.

### Create a personal access token for your Asana
Create a [Personal Access Token](https://developers.asana.com/docs/personal-access-token) in Asana. At Asana, we created a [Guest Account](https://asana.com/guide/help/organizations/guests) to run the random one on one script, so no engineer's personal access token is used, and it's clear that there's a specific "Random one on one bot" user who is making the task updates.

Copy this Personal Access Token for the next steps.

### Create an Asana project for the random one on ones
You will need to create an Asana project 
The project will be used to schedule and store upcoming random one on one meetings for participating members.

Make sure that you have created an Asana project with
- At least 2 sections named **Members** and **Upcoming**
- A task assigned to the user, owner of the personal access token, responsible for creating random one on ones

For each member, add a task to the **Member** section and assign to the corresponding user.
We recommend saving this project as a template, so that other groups can create their own Random one on one project easily.

### Run the script
`python oneonone.py --pat=<personal_access_token> --workspace-gid=<workspace_gid> --user-gid=<user_id> --task-name=<task_name>`
For further options run `python oneonone.py --help`

Have a happy random one on one

## Installing a Virtual Environment for Python

See [these instructions](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) for help in
setting up a virtual environment for Python, or use the following TL;DR version:

* run `python3 -m venv v-env` to create a virtual environment
* run `source v-env/bin/activate` to activate and enter your virtual environment
* once activated, run `deactivate` to deactivate and leave your virtual environment
