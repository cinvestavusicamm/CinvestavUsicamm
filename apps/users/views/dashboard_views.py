from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def dashboard(request):
    
    return render(request, 'index_docente.html')