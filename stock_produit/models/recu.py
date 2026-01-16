# models/recu.py
from django.db import models
from decimal import Decimal

class Recu(models.Model):
        numero = models.CharField(max_length=20, unique=True)
        total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
        created_at = models.DateTimeField(auto_now_add=True)

        def calculer_total(self):
            total = sum(vente.total_price for vente in self.ventes.all())
            self.total = total
            self.save()

        def __str__(self):
            return f"Reçu {self.numero}"
