from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from .models import Produit, Carton, Sale
from .models import User
from .forms import (
    ProduitForm,
    CartonForm,
    VenteForm,
    UserRegisterForm
)


def inscription(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserRegisterForm()

    return render(request, "Auth/inscription.html", {"form": form})


def connexion(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Email ou mot de passe incorrect")

    return render(request, "Auth/connexion.html")


@login_required
def deconnexion(request):
    logout(request)
    return redirect("connexion")


@login_required
def dashboard(request):
    produits = Produit.objects.count()
    ventes = Sale.objects.count()
    cartons = Carton.objects.count()

    return render(request, "Dashboard/index.html", {
        "produits": produits,
        "ventes": ventes,
        "cartons": cartons,
    })




@login_required
def produits(request):
    produits = Produit.objects.all()

    if request.method == "POST":
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("produits")
    else:
        form = ProduitForm()

    return render(request, "Produit/produits.html", {
        "produits": produits,
        "form": form,
    })


@login_required
def produits_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)

    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect("produits")
    else:
        form = ProduitForm(instance=produit)

    return render(request, "Produit/produits.html", {
        "form": form,
        "produit": produit,
        "produits": Produit.objects.all(),
    })




@login_required
def produits_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)

    if request.method == "POST":
        produit.delete()
        return redirect("produits")

    return render(request, "Produit/produits.html", {
        "produit": produit,
    })




@login_required
def cartons(request):
    cartons = Carton.objects.filter(is_sold_out=False)

    if request.method == "POST":
        form = CartonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("cartons")
    else:
        form = CartonForm()

    return render(request, "Carton/cartons.html", {
        "cartons": cartons,
        "form": form,
    })



@login_required
def cartons_update(request, pk):
    carton = get_object_or_404(Carton, pk=pk)

    if request.method == "POST":
        form = CartonForm(request.POST, instance=carton)
        if form.is_valid():
            form.save()
            return redirect("cartons")
    else:
        form = CartonForm(instance=carton)

    return render(request, "Carton/cartons.html", {
        "form": form,
        "carton": carton,
        "cartons": Carton.objects.filter(is_sold_out=False),
    })



@login_required
def cartons_delete(request, pk):
    carton = get_object_or_404(Carton, pk=pk)

    if request.method == "POST":
        carton.delete()
        return redirect("stock_produit:cartons")

    return render(request, "Carton/cartons.html", {
        "carton": carton,
    })







@login_required
def ventes(request):
    ventes = Sale.objects.select_related("produit", "carton").order_by("-created_at")

    if request.method == "POST":
        form = VenteForm(request.POST)
        if form.is_valid():
            sale = form.save()

            # Mise à jour du stock du carton
            if sale.carton:
                sale.carton.remaining_weight -= sale.weight_sold
                sale.carton.save()

            return redirect("stock_produit:ventes")
    else:
        form = VenteForm()

    return render(request, "Vente/ventes.html", {
        "ventes": ventes,
        "form": form,
    })



@login_required
def ventes_update(request, pk):
    vente = get_object_or_404(Sale, pk=pk)

    if request.method == "POST":
        form = VenteForm(request.POST, instance=vente)
        if form.is_valid():
            form.save()
            return redirect("stock_produit:ventes")
    else:
        form = VenteForm(instance=vente)

    return render(request, "Vente/ventes.html", {
        "form": form,
        "vente": vente,
        "ventes": Sale.objects.all(),
    })




@login_required
def ventes_delete(request, pk):
    vente = get_object_or_404(Sale, pk=pk)

    if request.method == "POST":
        vente.delete()
        return redirect("stock_produit:ventes")

    return render(request, "Vente/ventes.html", {
        "vente": vente,
    })








@login_required
def user_list(request):
    users = User.objects.all().order_by("-date_joined")

    return render(request, "User/utilisateurs.html", {
        "users": users
    })
