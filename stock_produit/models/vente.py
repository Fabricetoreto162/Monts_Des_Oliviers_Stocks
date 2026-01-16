from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from .produit import Produit
from .carton import Carton
from .recu import Recu


class Vente(models.Model):
    created_at = models.DateTimeField(null=True, blank=True)
    TYPE_VENTE_CHOICES = (
        ("DETAIL", "Détail (Kg)"),
        ("CARTON", "Carton entier"),
    )

    recu = models.ForeignKey(
        Recu,
        related_name="ventes",
        on_delete=models.CASCADE
    )

    produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT
    )

    carton = models.ForeignKey(
        Carton,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    type_vente = models.CharField(
        max_length=10,
        choices=TYPE_VENTE_CHOICES
    )

    poids_vendu = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    reduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    

    # ✅ VALIDATION MÉTIER
    def clean(self):
        if not self.carton:
            raise ValidationError({"carton": "Un carton est obligatoire."})

        if self.type_vente == "DETAIL" and not self.poids_vendu:
            raise ValidationError({"poids_vendu": "Poids requis pour une vente au détail."})

    # 💰 CALCUL DU TOTAL
    def save(self, *args, **kwargs):
        prix = Decimal(self.prix_unitaire or 0)
        reduction = Decimal(self.reduction or 0)

        if self.type_vente == "DETAIL":
            poids = Decimal(self.poids_vendu or 0)
            self.total_price = (poids * prix) - reduction
        else:
            self.total_price = prix - reduction

        if self.total_price < 0:
            self.total_price = Decimal("0")

        super().save(*args, **kwargs)

    # 📦 DÉDUCTION DU STOCK

    def update_stock(self):
        if not self.carton:
            raise ValidationError("Carton manquant pour la vente")

        # 🔹 Vente au détail (kg)
        if self.type_vente == "DETAIL":
            poids = Decimal(self.poids_vendu or 0)

            if poids <= 0:
                raise ValidationError("Poids invalide")

            if poids > self.carton.remaining_weight:
                raise ValidationError("Stock insuffisant dans le carton")

            self.carton.remaining_weight -= poids

        # 🔹 Vente carton entier
        else:
            self.carton.remaining_weight = Decimal("0")

        # 🔒 Sécurité
        if self.carton.remaining_weight <= 0:
            self.carton.remaining_weight = Decimal("0")
            self.carton.is_sold_out = True

        self.carton.save()

    # 🔄 RESTAURATION DU STOCK
    def restore_stock(self):
        if self.type_vente == "DETAIL":
            poids = Decimal(self.poids_vendu)
        else:
            poids = Decimal(self.carton.remaining_weight)

        self.carton.remaining_weight += poids
        self.carton.is_sold_out = False
        self.carton.save()
