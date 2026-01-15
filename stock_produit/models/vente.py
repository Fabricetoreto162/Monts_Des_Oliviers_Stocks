from django.db import models
from .produit import Produit
from .carton import Carton

class Sale(models.Model):
    SALE_TYPE_CHOICES = [
        ('detail', 'Détail'),
        ('carton', 'Carton'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    carton = models.ForeignKey(
        Carton,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    sale_type = models.CharField(max_length=10, choices=SALE_TYPE_CHOICES)
    weight_sold = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Mise à jour automatique du carton
        if self.carton and self.sale_type == 'detail':
            self.carton.remaining_weight -= self.weight_sold
            self.carton.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.name} - {self.total_price} FCFA"
