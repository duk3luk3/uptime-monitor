# coding=utf8
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from celery import Celery

class Group(models.Model):
  name = models.CharField(max_length=512)

  def __str__(self):
    return self.name

class Target(models.Model):
  hostname = models.CharField(max_length=512)
  description = models.CharField(max_length=512)
  auto_ping = models.BooleanField(default=False)
  group = models.ForeignKey(Group)

  def __str__(self):
    return "%s (%s)" % (self.hostname, self.description)

#  def save(self, *args, **kwargs):
#    super(Target, self).save(*args, **kwargs)
#        self.save()


class Uptime(models.Model):
  target = models.ForeignKey(Target)
  interval_start = models.DateTimeField()
  interval_end = models.DateTimeField()
  ping_average = models.FloatField()
  uptime_fraction = models.FloatField()

  def __str__(self):
    return u"%s up %.3f%% of the time between %s and %s with avg ping of %f" % (self.target.hostname, self.uptime_fraction*100, self.interval_start,self.interval_end,self.ping_average)

  @staticmethod
  def new(target):
    now = timezone.now()
    before = now - timedelta(seconds=120)
    pings = target.ping_set.filter(executed__gte=before)
    oldpings = target.ping_set.exclude(executed__gte=before)
    if pings.count() > 0:
      earliest = pings.earliest('executed')
      latest = pings.latest('executed')
      successful_pings = pings.filter(time__gte=0)
      ping_count = pings.count()
      successful_count = successful_pings.count()
      ping_average = successful_pings.aggregate(models.Avg('time'))['time__avg']
      uptime_fraction = float(successful_count) / ping_count
      return Uptime(target=target,interval_start=earliest.executed,interval_end=latest.executed,ping_average=ping_average,uptime_fraction=uptime_fraction), oldpings
    else:
      return None, None


class Ping(models.Model):
  target = models.ForeignKey(Target)
  executed = models.DateTimeField(auto_now_add=True)
  time = models.FloatField(default=-1)

  def was_successful(self):
    return self.time >= 0

  def __str__(self):
    return u"Ping to %s at %s ran in %f s" % (self.target.hostname, self.executed, self.time)

