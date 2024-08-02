from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
def index_auto(request):
    return JsonResponse({'s':4})
