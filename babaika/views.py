from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from babaika.models import Auto


# Create your views here.
def index_auto(request):
    qs = Auto.objects.all()
    return JsonResponse(qs)
