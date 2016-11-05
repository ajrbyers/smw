from django.core.management.base import BaseCommand, CommandError

from cron import models
from cron import execute_cron_tasks as ect

from pprint import pprint
import sys

class Command(BaseCommand):
    help = 'Actions cron tasks.'

    def add_arguments(self, parser):
        parser.add_argument('schedule', nargs='+', type=str)

    def handle(self, *args, **options):
        cron_tasks = models.CronTask.objects.filter(schedule__in=options['schedule'])

        for task in cron_tasks:

            if task.name == 'reminders':
                ect.remind_unaccepted_reviews(task)
                ect.remind_accepted_reviews(task)
                ect.remind_overdue_reviews(task)
                ect.reminder_overdue_revisions(task)
                ect.reminder_notifications_not_emailed(task)
