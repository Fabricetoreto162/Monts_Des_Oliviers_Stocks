from django.db import models
from .produit import Produit

class Carton(models.Model):
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='cartons'
    )
    initial_weight = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_weight = models.DecimalField(max_digits=10, decimal_places=2)
    is_sold_out = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.remaining_weight <= 0:
            self.is_sold_out = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.name} - {self.remaining_weight} kg"
