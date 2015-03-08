from django.shortcuts import render
from django.http import HttpResponse
from .models import Target

def index(request):
  #return HttpResponse("Hello, world. You're at the polls index.")
  targets = Target.objects.select_related('ping')

  for target in targets:
    try:
      target.last_ping = target.ping_set.latest('executed')
    except:
      target.last_ping = "No non-coalesced pings"

    target.last_uptime = target.uptime_set.latest('interval_end')

  return render(request, 'uptime/index.html', {'targets':targets})
