from django.contrib import admin
from .models import User, Produit, Carton, Vente

admin.site.register(User)
admin.site.register(Produit)
admin.site.register(Carton)
admin.site.register(Vente)
