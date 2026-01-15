from django.db import models
from .produit import Produit
from decimal import Decimal


class Carton(models.Model):
    produit = models.ForeignKey(
        Produit,
        related_name="cartons",
        on_delete=models.CASCADE
    )

    # ✅ POIDS INITIAL (Decimal)
    initial_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # ✅ POIDS RESTANT (Decimal)
    remaining_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    is_sold_out = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Initialisation automatique à la création
        if self.pk is None:
            self.remaining_weight = self.initial_weight

        # Mise à jour état stock
        self.is_sold_out = self.remaining_weight <= Decimal("0")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.name} - {self.remaining_weight} kg restants"
