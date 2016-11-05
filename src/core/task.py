from core import models

def create_new_task(book, creator, assignee, text, workflow=None):
    task = models.Task(book=book, creator=creator, assignee=assignee, text=text, workflow=workflow)
    task.save()
    return task

def create_new_general_task(creator, assignee, text, workflow=None):
    task = models.Task(book=None, creator=creator, assignee=assignee, text=text, workflow=workflow)
    task.save()
    return task
