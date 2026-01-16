from django.db import models
from decimal import Decimal
from .produit import Produit
from .carton import Carton


class Vente(models.Model):

    TYPE_VENTE_CHOICES = (
        ("DETAIL", "Détail (Kg)"),
        ("CARTON", "Carton entier"),
    )

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    carton = models.ForeignKey(Carton, on_delete=models.CASCADE)
    type_vente = models.CharField(max_length=10, choices=TYPE_VENTE_CHOICES)

    poids_vendu = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    reduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_stock(self):
        """
        Met à jour le stock du carton selon le type de vente
        """

        if self.type_vente == "DETAIL":
            poids = Decimal(self.poids_vendu)

        elif self.type_vente == "CARTON":
            poids = Decimal(self.carton.remaining_weight)

        else:
            return

        # 🔴 Sécurité : éviter stock négatif
        if poids > self.carton.remaining_weight:
            raise ValueError("Poids vendu supérieur au stock disponible")

        # ✅ Mise à jour du stock
        self.carton.remaining_weight -= poids

        if self.carton.remaining_weight <= 0:
            self.carton.remaining_weight = Decimal("0")
            self.carton.is_sold_out = True

        self.carton.save()

    def save(self, *args, **kwargs):
        # Calcul automatique du total
        if self.type_vente == "DETAIL":
            self.total_price = (
                self.poids_vendu * self.prix_unitaire
            ) - self.reduction
        else:
            self.total_price = self.prix_unitaire - self.reduction

        super().save(*args, **kwargs)



    def restore_stock(self):
        """
        Restaure le stock du carton lors de la suppression d'une vente
        """

        if self.type_vente == "DETAIL":
            poids = Decimal(self.poids_vendu)
        elif self.type_vente == "CARTON":
            poids = Decimal(self.carton.remaining_weight)
        else:
            return

        self.carton.remaining_weight += poids
        self.carton.is_sold_out = False
        self.carton.save()

