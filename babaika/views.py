from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from babaika.models import Auto

def index_auto(request):
    qs = Auto.objects.all()
    print(qs)
    d = []
    for i in qs:
        d.append(f'name:{i.name}')
    return JsonResponse(d, safe=False)
