from django.shortcuts import render, get_object_or_404
from .models import Aluguer

def comprovativo_aluguer(request, aluguer_id):  # <--- MUDAR DE 'id' PARA 'aluguer_id'
    # Nota que aqui também tens de mudar 'id=' para 'id=aluguer_id' ou 'pk=aluguer_id'
    aluguer = get_object_or_404(Aluguer, id=aluguer_id)
    
    return render(request, 'comprovativo.html', {'aluguer': aluguer})