from celery import task
from ping import do_one
from models import Target

@task()
def ping(target_id):
  target = Target.objects.get(pk=target_id)
  time = do_one(target.hostname,2000)
  if time == None:
    time = -1
  target.ping_set.create(time=time)

