from django.contrib import admin
from .models import Nature, AccessoireHistorique, Accessoire, BatterieHistorique, Batterie, Client, Pneu, PneuHistorique, Fournisseur, Historique, Administrateur, Marque, Numero, Transaction

# Register your models here.

admin.site.register(Pneu)
admin.site.register(PneuHistorique)
admin.site.register(Fournisseur)
admin.site.register(Historique)
admin.site.register(Client)
admin.site.register(Administrateur)
admin.site.register(Marque)
admin.site.register(Numero)
admin.site.register(Transaction)
admin.site.register(Nature)
admin.site.register(Accessoire)
admin.site.register(AccessoireHistorique)
admin.site.register(BatterieHistorique)
admin.site.register(Batterie)
