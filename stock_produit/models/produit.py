from django.db import models

class Produit(models.Model):
    CATEGORY_CHOICES = [
        ('volaille', 'Volailles'),
        ('poisson', 'Poissons'),
        ('frites', 'Frites'),
    ]

    name = models.CharField(max_length=100)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    carton_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    stock_alert = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
