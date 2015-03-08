from __future__ import absolute_import

from datetime import datetime, timedelta
from celery import task
from django.db.models import Count
from django.utils import timezone
from .models import Target, Uptime, Ping
from .ping import do_one

@task()
def ping():
  targets = Target.objects.filter(auto_ping=True)
  pings_done = 0
  for target in targets:
    doping = True
    try:
      lastping = target.ping_set.latest('executed').executed
      if timezone.now() - lastping <= timedelta(seconds=15):
        doping = False
    except:
      pass
    if doping:
      time = do_one(target.hostname,2000)
      pings_done = pings_done+1
      if time == None:
        time = -1
      target.ping_set.create(time=time)
  return pings_done

@task()
def coalesce():
  targets = Target.objects.all()
  for target in targets:
    uptime, oldpings = Uptime.new(target)
    if uptime:
      uptime.save()
      oldpings.delete()
