from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from django.db import transaction
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Count, Q, F, Sum,Case,When,DecimalField
from decimal import Decimal





from decimal import Decimal

from .models import Vente, Recu
def generer_numero_recu():
        date_str = now().strftime("%Y%m%d")
        count = Recu.objects.filter(numero__startswith=date_str).count() + 1
        return f"{date_str}-{count:04d}"

from .forms import VenteForm
from django.db.models import Sum, Count, F
from django.db.models import  Q
from django.contrib import messages
from datetime import date, datetime, timedelta


from .models import Produit, Carton, Vente,Recu
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
    ventes_jour = Vente.objects.filter(recu__created_at__date=date)

    total_jour = ventes_jour.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    # 🔹 CHIFFRE D'AFFAIRE MENSUEL
    chiffre_affaire_mois = Vente.objects.filter(
        recu__created_at__year=date.year,
        recu__created_at__month=date.month
    ).aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0")

    # 🔹 PRODUITS DISPONIBLES
   # 🔹 PRODUITS + ÉTAT DES CARTONS
    produits_disponibles = Produit.objects.annotate(

    # 🟢 Cartons encore disponibles
    cartons_restants=Count(
        "cartons",
        filter=Q(cartons__is_sold_out=False)
    ),

    # 🟡 Cartons en cours de vente
    cartons_en_cours=Count(
        "cartons",
        filter=Q(
            cartons__remaining_weight__gt=0,
            cartons__remaining_weight__lt=F("cartons__initial_weight")
        )
    ),

    # 🔵 Cartons pleins
    cartons_pleins=Count(
        "cartons",
        filter=Q(
            cartons__remaining_weight=F("cartons__initial_weight")
        )
    ),
)



    total_produits = produits_disponibles.count()
    total_cartons = Carton.objects.filter(is_sold_out=False).count()

    # 🔹 STOCKS FAIBLES
    stocks_faibles = produits_disponibles.filter(
        cartons_restants__lte=F("stock_alert")
    )


    context = {
        "selected_date": date,
        "total_jour": total_jour,
        "chiffre_affaire_mois": chiffre_affaire_mois,
        "total_produits": produits_disponibles.count(),
        "total_cartons": Carton.objects.filter(is_sold_out=False).count(),
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




@login_required
def ventes(request, recu_id=None):

    # ================== MODE DÉTAIL REÇU ==================
    if recu_id:
        recu = get_object_or_404(
            Recu.objects.prefetch_related("ventes"),
            pk=recu_id
        )

        context = {
            "recu": recu,
            "form": VenteForm(),
            "panier": [],
            "recus": [],
            "total_jour": Decimal("0"),
            "selected_date": None,
            "detail_recu": True,
        }

        return render(request, "Vente/ventes.html", context)

    # ================== MODE CAISSE (NORMAL) ==================
    date_str = request.GET.get("date")

    if date_str:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        date_obj = timezone.now().date()

    selected_date = date_obj.strftime("%Y-%m-%d")

    # 🔹 Reçus du jour
    recus = Recu.objects.filter(
        created_at__date=date_obj
    ).prefetch_related("ventes").order_by("-id")

    # 🔹 Total journalier
    total_jour = recus.aggregate(
        total=Sum("total")
    )["total"] or Decimal("0")

    context = {
        "form": VenteForm(),
        "panier": request.session.get("panier", []),
        "recus": recus,
        "total_jour": total_jour,
        "selected_date": selected_date,
        "detail_recu": False,
    }

    return render(request, "Vente/ventes.html", context)





@login_required
def detail_recu(request, recu_id):
    recu = get_object_or_404(
        Recu.objects.prefetch_related("detail_recu"),
        id=recu_id
    )

    return render(request, "Vente/ventes.html", {
        "recu": recu
    })


@login_required
@require_POST
def ajouter_au_panier(request):
    try:
        data = json.loads(request.body)

        produit = Produit.objects.get(id=data["produit_id"])
        carton = Carton.objects.get(id=data["carton_id"])

        poids = Decimal(data["poids_vendu"]) if data.get("poids_vendu") else Decimal("1")
        prix = Decimal(data["prix_unitaire"])
        reduction = Decimal(data.get("reduction", 0))

        total = (poids * prix) - reduction

        panier = request.session.get("panier", [])

        panier.append({
            "produit_id": produit.id,
            "produit_nom": produit.name,
            "carton_id": carton.id,
            "type_vente": data["type_vente"],
            "poids_vendu": data.get("poids_vendu"),
            "prix_unitaire": str(prix),
            "reduction": str(reduction),
            "total_price": str(total),
        })

        request.session["panier"] = panier
        request.session.modified = True

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@transaction.atomic
def valider_panier(request):
        panier = request.session.get("panier", [])

        # 1️⃣ PANIER VIDE
        if not panier:
            messages.error(request, "Le panier est vide.")
            return redirect("ventes")

        # 2️⃣ CRÉATION DU REÇU
        recu = Recu.objects.create(
            numero=generer_numero_recu(),
            total=Decimal("0")
        )

        total_recu = Decimal("0")

        # 3️⃣ TRAITEMENT DE CHAQUE LIGNE DU PANIER
        for index, item in enumerate(panier, start=1):

            # 🔐 SÉCURISATION DES DONNÉES
            produit_id = item.get("produit_id")
            carton_id = item.get("carton_id")
            type_vente = item.get("type_vente")

            if not produit_id or not carton_id or not type_vente:
                messages.error(
                    request,
                    f"Ligne {index} invalide dans le panier (données manquantes)."
                )
                raise Exception("Panier invalide")

            produit = Produit.objects.get(id=produit_id)
            carton = Carton.objects.get(id=carton_id)

            # ⚖️ POIDS SELON TYPE DE VENTE
            if type_vente == "DETAIL":
                poids_brut = item.get("poids_vendu")
                if not poids_brut:
                    messages.error(
                        request,
                        f"Poids manquant pour la vente au détail (ligne {index})."
                    )
                    raise Exception("Poids manquant")

                poids_vendu = Decimal(poids_brut)
            else:
                poids_vendu = None

            # 💰 PRIX & RÉDUCTION
            prix_unitaire = Decimal(item.get("prix_unitaire", 0))
            reduction = Decimal(item.get("reduction", 0))

            # 4️⃣ CRÉATION DE LA VENTE
            vente = Vente.objects.create(
                recu=recu,
                produit=produit,
                carton=carton,
                type_vente=type_vente,
                poids_vendu=poids_vendu,
                prix_unitaire=prix_unitaire,
                reduction=reduction,
            )

            # 5️⃣ MISE À JOUR DU STOCK
            vente.update_stock()

            total_recu += vente.total_price

        # 6️⃣ TOTAL DU REÇU
        recu.total = total_recu
        recu.save()

        # 7️⃣ VIDAGE DU PANIER
        request.session["panier"] = []
        request.session.modified = True

        messages.success(request, "Vente enregistrée avec succès.")
        return redirect("detail_recu", recu_id=recu.id)

@login_required
def vider_panier(request):
    request.session["panier"] = []
    request.session.modified = True
    messages.success(request, "🗑️ Panier vidé")
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























def rapport_journalier(request):

    selected_date = request.GET.get("date")
    if selected_date:
        date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        date = timezone.now().date()

    # 🔹 Regrouper par produit
    ventes = (
        Vente.objects
        .filter(recu__created_at__date=date)
        .values('produit__name')
        .annotate(
            total_quantite=Sum(
                Case(
                    When(type_vente='DETAIL', then=F('poids_vendu')),
                    When(type_vente='CARTON', then=F('carton__initial_weight')),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            total_montant=Sum('total_price')
        )
        .order_by('produit__name')
    )

    total_detail = (
        Vente.objects
        .filter(recu__created_at__date=date, type_vente='DETAIL')
        .aggregate(total=Sum('total_price'))['total'] or 0
    )

    total_carton = (
        Vente.objects
        .filter(recu__created_at__date=date, type_vente='CARTON')
        .aggregate(total=Sum('total_price'))['total'] or 0
    )

    total_general = total_detail + total_carton

    context = {
        'date': date,
        'selected_date': date,   # ✅ AJOUT IMPORTANT
        'ventes': ventes,
        'total_detail': total_detail,
        'total_carton': total_carton,
        'total_general': total_general,
    }

    return render(request, "Rapport/rapport_journalier.html", context)















def rapport_semaine(request):
    week_value = request.GET.get("week")  # Format attendu : "2026-W06"

    if week_value:
        # Extraire année et numéro de semaine
        year, week_num = map(int, week_value.split('-W'))
        # Calcul du lundi de la semaine
        start_date = date.fromisocalendar(year, week_num, 1)
        # Calcul du dimanche de la semaine
        end_date = start_date + timedelta(days=6)
    else:
        # Par défaut semaine en cours
        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # lundi
        end_date = start_date + timedelta(days=6)  # dimanche

    # 🔹 Regrouper par produit
    ventes = (
        Vente.objects
        .filter(recu__created_at__date__range=(start_date, end_date))
        .values('produit__name')
        .annotate(
            total_quantite=Sum(
                Case(
                    When(type_vente='DETAIL', then=F('poids_vendu')),
                    When(type_vente='CARTON', then=F('carton__initial_weight')),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            total_montant=Sum('total_price')
        )
        .order_by('produit__name')
    )

    # 🔹 Totaux généraux
    total_detail = (
        Vente.objects
        .filter(recu__created_at__date__range=(start_date, end_date), type_vente='DETAIL')
        .aggregate(total=Sum('total_price'))['total'] or 0
    )

    total_carton = (
        Vente.objects
        .filter(recu__created_at__date__range=(start_date, end_date), type_vente='CARTON')
        .aggregate(total=Sum('total_price'))['total'] or 0
    )

    total_general = total_detail + total_carton

    context = {
        'ventes': ventes,
        'total_detail': total_detail,
        'total_carton': total_carton,
        'total_general': total_general,
        'start_date': start_date,
        'end_date': end_date,
        'selected_week': week_value,
    }

    return render(request, "Rapport/rapport_semaine.html", context)