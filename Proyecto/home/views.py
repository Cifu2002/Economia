from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home/home.html')
def cuentas(request):
    return render(request,'home/cuentas.html')
def terminos(request):
    return render(request,'home/terminos.html')
def nuevo(request):
    return render(request,'home/nuevo.html')