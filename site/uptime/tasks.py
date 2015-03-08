from __future__ import absolute_import

from datetime import datetime
from celery import task
from .models import Target, Uptime, Ping
from .ping import do_one

@task()
def ping(target_id):
  target = Target.objects.get(pk=target_id)
  time = do_one(target.hostname,2000)
  if time == None:
    time = -1
  target.ping_set.create(time=time)

@task()
def coalesce(target_id):
  target = Target.objects.get(pk=target_id)
  uptime, pings = Uptime.new(target, 0, datetime.now())
  uptime.save()
  pings.delete()
