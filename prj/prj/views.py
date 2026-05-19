from django.shortcuts import render

def home(request):
    return render(request, "index.html")

def api_playground(request):
    return render(request, 'api_playground.html')
