from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Produit, Carton, Vente, User

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            "name",
            "price_per_kg",
            "carton_price",
            "category",
            "stock_alert",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nom du produit (ex: Poulet entier)"
            }),
            "price_per_kg": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Prix par Kg (FCFA)"
            }),
            "carton_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Prix du carton (FCFA)"
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "stock_alert": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Seuil d’alerte stock (cartons)"
            }),
        }




from django import forms
from .models import Carton


class CartonForm(forms.ModelForm):
    class Meta:
        model = Carton
        fields = ["produit", "initial_weight"]  # ✅ on enlève remaining_weight

        widgets = {
            "produit": forms.Select(attrs={
                "class": "form-select"
            }),
            "initial_weight": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Poids initial (Kg)",
                "step": "0.01"
            }),
        }





class VenteForm(forms.ModelForm):

    class Meta:
        model = Vente
        fields = [
            "produit",
            "carton",
            "type_vente",
            "poids_vendu",
            "prix_unitaire",
            "reduction",
        ]

        widgets = {
            "produit": forms.Select(attrs={
                "class": "form-select"
            }),
            "carton": forms.Select(attrs={
                "class": "form-select"
            }),
            "type_vente": forms.Select(attrs={
                "class": "form-select"
            }),
            "poids_vendu": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Poids vendu (Kg)"
            }),
            "prix_unitaire": forms.NumberInput(attrs={
                "class": "form-control",
                "readonly": True
            }),
            "reduction": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Réduction"
            }),
        }

    def clean(self):
        """
        Validation intelligente selon le type de vente
        """
        cleaned_data = super().clean()

        type_vente = cleaned_data.get("type_vente")
        poids_vendu = cleaned_data.get("poids_vendu")

        if type_vente == "DETAIL" and not poids_vendu:
            self.add_error(
                "poids_vendu",
                "Le poids est obligatoire pour une vente au détail"
            )

        if type_vente == "CARTON":
            cleaned_data["poids_vendu"] = None

        return cleaned_data

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "user_type", "password1", "password2")

        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Adresse email"
            }),
            "user_type": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Mot de passe"
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirmer le mot de passe"
        })
