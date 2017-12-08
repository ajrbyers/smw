from django.db import models


def cron_schedule():
    return (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    )


class CronTask(models.Model):

    name = models.CharField(
        max_length=100,
    )
    enabled = models.BooleanField(
        default=True,
    )
    schedule = models.CharField(
        max_length=20,
        choices=cron_schedule(),
    )
    note = models.TextField(
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name
