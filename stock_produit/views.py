from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone

from django.db import transaction
from django.http import JsonResponse

from decimal import Decimal

from .models import Vente
from .forms import VenteForm
from django.db.models import Sum, Count, F
from django.db.models import  Q
from django.contrib import messages
from datetime import datetime

from .models import Produit, Carton, Vente
from .models import User
from .forms import (
    ProduitForm,
    CartonForm,
    UserRegisterForm
)


def inscription(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("connexion")
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
    # 📅 Date sélectionnée
    selected_date = request.GET.get("date")

    if selected_date:
        date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        date = timezone.now().date()

    # 🔹 VENTES DU JOUR
    ventes_jour = Vente.objects.filter(created_at__date=date)
    total_jour = ventes_jour.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    # 🔹 CHIFFRE D'AFFAIRE MENSUEL
    chiffre_affaire_mois = Vente.objects.filter(
        created_at__year=date.year,
        created_at__month=date.month
    ).aggregate(
        total=Sum("total_price")
    )["total"] or 0

    # 🔹 PRODUITS DISPONIBLES
    produits_disponibles = Produit.objects.annotate(
    cartons_disponibles=Count(
        "cartons",
        filter=Q(cartons__is_sold_out=False)
    )
)


    total_produits = produits_disponibles.count()
    total_cartons = Carton.objects.filter(is_sold_out=False).count()

    # 🔹 STOCKS FAIBLES
    stocks_faibles = produits_disponibles.filter(
        cartons_disponibles__lte=F("stock_alert")
    )

    context = {
        "selected_date": date,
        "total_jour": total_jour,
        "chiffre_affaire_mois": chiffre_affaire_mois,
        "total_produits": total_produits,
        "total_cartons": total_cartons,
        "stocks_faibles": stocks_faibles,
    }

    return render(request, "Dashboard/index.html", context)




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




# 🔹 LISTE + CRÉATION
@login_required
def cartons(request):
    form = CartonForm()

    if request.method == "POST":
        form = CartonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("cartons")

    cartons = Carton.objects.select_related("produit")

    produits_groupes = {}

    for carton in cartons:
        produit = carton.produit

        if produit.id not in produits_groupes:
            produits_groupes[produit.id] = {
                "produit": produit,
                "cartons": [],
                "nombre_cartons": 0,
                "total_weight": 0,
                "stock_faible": False,
            }

        produits_groupes[produit.id]["cartons"].append(carton)
        produits_groupes[produit.id]["nombre_cartons"] += 1
        produits_groupes[produit.id]["total_weight"] += carton.remaining_weight or 0

    for item in produits_groupes.values():
        if item["nombre_cartons"] <= item["produit"].stock_alert:
            item["stock_faible"] = True

    context = {
        "produits_groupes": produits_groupes.values(),
        "form": form,
        "carton_edit": None,
    }

    return render(request, "Carton/cartons.html", context)


# 🔹 MODIFICATION
@login_required
def cartons_update(request, id):
    carton = get_object_or_404(Carton, id=id)

    if request.method == "POST":
        form = CartonForm(request.POST, instance=carton)
        if form.is_valid():
            form.save()
            return redirect("cartons")
    else:
        form = CartonForm(instance=carton)

    cartons = Carton.objects.select_related("produit")

    produits_groupes = {}
    for c in cartons:
        produit = c.produit
        if produit.id not in produits_groupes:
            produits_groupes[produit.id] = {
                "produit": produit,
                "cartons": [],
                "nombre_cartons": 0,
                "total_weight": 0,
                "stock_faible": False,
            }

        produits_groupes[produit.id]["cartons"].append(c)
        produits_groupes[produit.id]["nombre_cartons"] += 1
        produits_groupes[produit.id]["total_weight"] += c.remaining_weight or 0

    context = {
        "produits_groupes": produits_groupes.values(),
        "form": form,
        "carton_edit": carton,
    }

    return render(request, "Carton/cartons.html", context)


# 🔹 SUPPRESSION
@login_required
def cartons_delete(request, id):
    carton = get_object_or_404(Carton, id=id)
    carton.delete()
    return redirect("cartons")




def ventes(request):
    # 📅 Date sélectionnée
    date_str = request.GET.get("date")

    if date_str:
        selected_date = date_str
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        date_obj = timezone.now().date()
        selected_date = date_obj.strftime("%Y-%m-%d")

    # 📦 Ventes du jour sélectionné
    ventes = Vente.objects.filter(created_at__date=date_obj).order_by("-created_at")

       # 💰 Total journalier
    total_jour = ventes.aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0")


    if request.method == "POST":
        form = VenteForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    vente = form.save(commit=False)

                    # 🔒 Conversion sécurité Decimal
                    vente.prix_unitaire = Decimal(vente.prix_unitaire)
                    vente.reduction = Decimal(vente.reduction or 0)

                    if vente.type_vente == "DETAIL":
                        vente.poids_vendu = Decimal(vente.poids_vendu)
                    else:
                        vente.poids_vendu = None

                    # 💾 Sauvegarde vente
                    vente.save()

                    # 🔄 Mise à jour stock carton
                    vente.update_stock()

                    messages.success(
                        request,
                        "✅ Vente enregistrée avec succès"
                    )

                    return redirect("ventes")

            except ValueError as e:
                messages.error(request, str(e))

        else:
            messages.error(request, "❌ Formulaire invalide")

    else:
        form = VenteForm()

    context = {
        "form": form,
        "ventes": ventes,
        "nombre_ventes": ventes.count(),
        "total_jour": total_jour,
        "selected_date": selected_date, 
    }

    return render(request, "Vente/ventes.html", context)



@login_required
def vente_update(request, pk):
    sale = get_object_or_404(Vente, pk=pk)
    form = VenteForm(instance=sale)

    if request.method == "POST":
        form = VenteForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect("ventes")

    return render(request, "Vente/ventes.html", {
        "form": form,
        "ventes": Vente.objects.all(),
        "edit_mode": True,
        "sale_id": pk
    })


@login_required
def vente_delete(request, pk):
    sale = get_object_or_404(Vente, pk=pk)

    with transaction.atomic():
        sale.restore_stock()   # 🔁 RESTAURATION
        sale.delete()          # ❌ SUPPRESSION

    return redirect("ventes")



@login_required
def get_prix_unitaire(request):
    produit_id = request.GET.get("produit")
    type_vente = request.GET.get("type")

    prix = 0

    if produit_id and type_vente:
        produit = Produit.objects.get(id=produit_id)

        if type_vente == "DETAIL":
            prix = produit.price_per_kg
        elif type_vente == "CARTON":
            prix = produit.carton_price

    return JsonResponse({"prix": float(prix)})



@login_required
def user_list(request):
    users = User.objects.all().order_by("-date_joined")

    return render(request, "User/utilisateurs.html", {
        "users": users
    })