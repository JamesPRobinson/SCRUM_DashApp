import asana
import datetime as dt  # The people who made the module datetime, also called the class datetime

PROJECT_ID = "...your project id here"
ACCESS_TOKEN = "...your token here"

def format_date(s):
    return str(dt.datetime.strptime(s[:10], '%Y-%m-%d').date())


def get_sprint_data(base_date):
    # Sections we're taking tasks from in Asana
    do_sections = ['Do', 'Doing', 'Sprint Backlog']

    # Access authentication for Asana (replace with OAuth?)
    proj_id = PROJECT_ID
    client = asana.Client.access_token(ACCESS_TOKEN)

    # Get Asana Section Boards (...by way of then grabbing associated tasks)
    sections = client.sections.get_sections_for_project(proj_id)

    # Values for our snapshot of Asana today
    tasks_remaining = total_cost = completed_tasks = 0

    for section in sections:
        if section['name'] in do_sections:
            sect_tasks = client.tasks.get_tasks_for_section(section['gid'])
            for doing_task in sect_tasks:
                data = client.tasks.get_task(doing_task['gid'])
                tasks_remaining += 1
                custom_fields = [e for e in data['custom_fields'] if e['name'] == 'Cost']
                for field in custom_fields:
                    if field['number_value']:
                        total_cost += int(field['number_value'])

        if section['name'] == 'Done':
            done_tasks = client.tasks.get_tasks_for_section(section['gid'])
            for done_task in done_tasks:
                data = client.tasks.get_task(done_task['gid'])
                if data['completed_at']:
                    if format_date(data['completed_at']) == base_date:
                        completed_tasks += 1

    return {'Date': base_date,
            'CompletedTasks': completed_tasks,
            'RemainingTasks': tasks_remaining,
            'RemainingEffort': total_cost,
            }
