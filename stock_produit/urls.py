from django.contrib import admin
from django.urls import path
from . import views 


urlpatterns = [

    # ================= AUTH =================
    path("", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),

    # ================= DASHBOARD =================
    path("index/", views.dashboard, name="dashboard"),

    # ================= PRODUITS =================
    path("produits/", views.produits, name="produits"),
    path("produits/<int:pk>/modifier/", views.produits_update, name="produits_update"),
    path("produits/<int:pk>/supprimer/", views.produits_delete, name="produits_delete"),

    # ================= CARTONS =================
    path("cartons/", views.cartons, name="cartons"),
    path("cartons/update/<int:id>/", views.cartons_update, name="cartons_update"),
    path("cartons/delete/<int:id>/", views.cartons_delete, name="cartons_delete"),
   
    # ================= VENTES =================
    path("ventes/", views.ventes, name="ventes"),
    path("ventes/<int:pk>/update/", views.vente_update, name="vente_update"),
    path("ventes/<int:pk>/delete/", views.vente_delete, name="vente_delete"),
    path("ajax/prix/", views.get_prix_unitaire, name="get_prix_unitaire"),
    # ================= UTILISATEURS =================
    path("utilisateurs/", views.user_list, name="users"),

  

]
