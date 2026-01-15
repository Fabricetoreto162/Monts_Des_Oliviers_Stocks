from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Produit, Carton, Sale, User

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



class CartonForm(forms.ModelForm):
    class Meta:
        model = Carton
        fields = ["produit", "initial_weight"]

        widgets = {
            "produit": forms.Select(attrs={
                "class": "form-select"
            }),
            "initial_weight": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Poids initial du carton (Kg)"
            }),
        }



class VenteForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            "produit",
            "carton",
            "sale_type",
            "weight_sold",
            "unit_price",
            "discount",
        ]

        widgets = {
            "produit": forms.Select(attrs={
                "class": "form-select"
            }),
            "carton": forms.Select(attrs={
                "class": "form-select"
            }),
            "sale_type": forms.Select(attrs={
                "class": "form-select"
            }),
            "weight_sold": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Poids vendu (Kg)"
            }),
            "unit_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Prix unitaire (FCFA)"
            }),
            "discount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Réduction (FCFA)",
                "value": 0
            }),
        }




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
