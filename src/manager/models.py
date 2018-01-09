from django.db import models
from django.contrib.auth.models import User


def group_types():
    return (
        ('editorial_group', 'Editorial Group'),
        ('review_committee', 'Review Committee'),
        ('generic', 'Generic'),
    )


class Group(models.Model):

    class Meta:
        ordering = ('sequence', 'name')

    group_type = models.CharField(
        max_length=20,
        choices=group_types(),
    )
    name = models.CharField(
        max_length=200,
    )
    active = models.BooleanField(
        default=True,
    )
    sequence = models.IntegerField()

    def __unicode__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u'%s' % self.name


class GroupMembership(models.Model):

    class Meta:
        ordering = ('sequence', 'added')

    group = models.ForeignKey(
        Group,
    )
    user = models.ForeignKey(
        User,
    )
    added = models.DateField(
        auto_now=True,
    )
    sequence = models.IntegerField()
