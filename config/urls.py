from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


# Importa a tua view nova
from core.views import comprovativo_aluguer 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # NOVA ROTA: ex: /aluguer/1/imprimir/
    path('aluguer/<int:aluguer_id>/imprimir/', comprovativo_aluguer, name='imprimir_aluguer'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)