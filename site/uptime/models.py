# coding=utf8
from django.db import models
from djcelery.models import PeriodicTask, IntervalSchedule, PERIOD_CHOICES

# Create your models here.

class Target(models.Model):
  hostname = models.CharField(max_length=512)
  description = models.CharField(max_length=512)
  auto_ping = models.BooleanField()
  ping_task = models.OneToOneField(PeriodicTask, blank=True, null=True)

  def __unicode__(self):
    return "%s (%s)" % (self.hostname, self.description)

  def save(self, *args, **kwargs):
    super(Target, self).save(*args, **kwargs)
    if self.auto_ping:
      if self.ping_task == None:
        tasks = PeriodicTask.objects.filter(name=self.hostname + " Auto Ping")
        if len(tasks) >= 1:
          self.ping_task = tasks[0]
        else:
          interval = IntervalSchedule.objects.filter(pk=1)
          if len(interval) < 1:
            interval = IntervalSchedule(every=10,period='seconds')
            interval.save()
          else:
            interval = interval[0]
          
          self.ping_task = PeriodicTask(
              name = self.hostname + " Auto Ping",
              task = "uptime.tasks.ping",
              interval = interval,
              args = [self.id],
              enabled = True,
              description = "Auto Ping for " + self.description
              )
          self.ping_task.save()
        self.save()

class Uptime(models.Model):
  target = models.ForeignKey(Target)
  interval_start = models.DateTimeField()
  interval_end = models.DateTimeField()
  ping_average = models.FloatField()
  uptime_fraction = models.FloatField()

  def __unicode__(self):
    return u"%s up %.3f%% of the time between %s and %s with avg ping of %f" % (self.target.hostname, self.uptime_fraction*100, self.interval_start,self.interval_end,self.ping_average)

  @staticmethod
  def new(target, interval_start, interval_end):
    pings = target.ping_set.filter(executed__range=(interval_start,interval_end))
    successful_pings = pings.filter(time__gte=0)
    ping_count = pings.count()
    successful_count = successful_pings.count()
    ping_average = successful_pings.aggregate(models.Avg('time'))['time__avg']
    uptime_fraction = float(successful_count) / ping_count
    return Uptime(target=target,interval_start=interval_start,interval_end=interval_end,ping_average=ping_average,uptime_fraction=uptime_fraction)


class Ping(models.Model):
  target = models.ForeignKey(Target)
  executed = models.DateTimeField(auto_now_add=True)
  time = models.FloatField(default=-1)

  def was_successful(self):
    return self.time >= 0

  def __unicode__(self):
    return u"Ping to %s at %s ran in %f s" % (self.target.hostname, self.executed, self.time)

