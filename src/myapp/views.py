from django.db.models import F, ExpressionWrapper, DecimalField, Count, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Client, Nature, Accessoire, AccessoireHistorique, Batterie, BatterieHistorique, Pneu, PneuHistorique, Fournisseur, Historique, Administrateur, Marque, Numero, Transaction
import decimal


def sortie(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    if admin is not None:
        if request.method == "POST":
            name_client = request.POST.get("name_client")
            contact_client = request.POST.get("contact_client")
            nombre_lignes = int(request.POST.get("nombre_de_lignes"))
            date = request.POST.get("date")
            montant_paye_total = float(request.POST.get("montant_paye"))
            montant_total_precedent = 0
            montant_restant_precedent = 0
            client = None
            for i in range(1, nombre_lignes + 1):
                marque = request.POST.get(f"marque_{i}")
                numero = request.POST.get(f"numero_{i}")
                try:
                    numero_ = Numero.objects.get(Numero=numero)
                except Numero.DoesNotExist:
                    message = "Le Numero n'existe pas !!"
                    return render(request, sortie.html, {"message": message})
                nature = request.POST.get(f"nature_{i}")
                details = request.POST.get(f"details_{i}")
                if details is None:
                    details = ""
                prix = float(request.POST.get(f"prix_{i}"))
                quantite = int(request.POST.get(f"quantite_{i}"))
                montant_total = float(prix * quantite)
                if i > 1:
                    client = Client.objects.get(Contact=contact_client)
                    if montant_restant_precedent > 0:
                        montant_paye_total = 0
                    else:
                        montant_paye_total -= montant_total_precedent
                    montant_restant = float(montant_total - montant_paye_total)
                    if montant_restant > 0:
                        client.Statut = False
                        client.save()
                    else:
                        client.Statut = True
                        client.save()
                else:
                    montant_restant = float(montant_total - montant_paye_total)
                montant_restant_precedent = montant_restant
                montant_total_precedent = montant_total
                designation = f"{nature} {marque} {numero} {details}"
                marque_saisie = Marque.objects.get(Nom=marque)
                numero_saisie = Numero.objects.get(Numero=numero)
                nature_ = Nature.objects.get(Name=nature)
                quantite_numero = numero_saisie.Quantite - quantite
                quantite_marque = marque_saisie.Quantite - quantite
                if (quantite_marque < 0 or marque_saisie.Quantite == 0) and (quantite_numero < 0 or numero_saisie.Quantite == 0):
                    message = "Quantité Stocks insuffisant !!"
                    context = {
                        "quantite_null": message
                    }
                    return render(request, "sortie.html", context=context)
                else:
                    if nature_.Name == "Pneu":
                        try:
                            pneu = Pneu.objects.get(Marque=marque_saisie, Numero=numero_saisie, Details__icontains=details)
                        except Pneu.DoesNotExist:
                            message = "Pneu non existant"
                            context = {"error_pneu": message}
                            return render(request, "sortie.html", context)
                        if pneu is not None:
                            if pneu.Quantite <= 0 or pneu.Quantite < quantite:
                                message = f"Quantité de pneu insuffisant ! Il reste {pneu.Quantite} pneu(s)"
                                context = {"error_pneu": message}
                                return render(request, "sortie.html", context)
                            else:
                                pneu.Quantite -= quantite
                                pneu.save()
                    elif nature_.Name == "Batterie":
                        try:
                            batterie = Batterie.objects.get(Marque=marque_saisie, Numero=numero_saisie, Details__icontains=details)
                        except Batterie.DoesNotExist:
                            message = "Batterie non existant"
                            context = {"error_pneu": message}
                            return render(request, "sortie.html", context)
                        if batterie is not None:
                            if batterie.Quantite <= 0 or batterie.Quantite  < quantite:
                                message = f"Quantité de batterie insuffisant ! Il reste {batterie.Quantite} batterie(s)"
                                context = {"error_pneu": message}
                                return render(request, "sortie.html", context)
                            else:
                                batterie.Quantite -= quantite
                                batterie.save()
                    else:
                        try:
                            accessoire = Accessoire.objects.get(Marque=marque_saisie, Numero=numero_saisie, Details__icontains=details)
                        except Accessoire.DoesNotExist:
                            message = "Accessoire non existant"
                            context = {"error_pneu": message}
                            return render(request, "sortie.html", context)
                        if accessoire is not None:
                            if accessoire.Quantite <= 0 or accessoire.Quantite  < quantite:
                                message = f"Quantité d'accessoire insuffisant ! Il reste {accessoire.Quantite} accessoire(s)"
                                context = {"error_pneu": message}
                                return render(request, "sortie.html", context)
                            else:
                                accessoire.Quantite -= quantite
                                accessoire.save()
                    marque_saisie.Quantite = quantite_marque
                    marque_saisie.save()
                    numero_saisie.Quantite = quantite_numero
                    numero_saisie.save()
                if name_client is not None and contact_client is not None:
                    try:
                        client = Client.objects.get(Contact=contact_client)
                    except Client.DoesNotExist:
                        statut = True
                        if montant_restant > 0:
                            statut = False
                        client = Client.objects.create(
                            Nom=name_client,
                            Contact=contact_client,
                            Statut=statut
                        )
                    history = Historique.objects.create(
                        Date_Achat=date,
                        Designation=designation,
                        Montant_Total=montant_total,
                        Montant_Paye=montant_paye_total,
                        Montant_Restant=montant_restant,
                        Client=client
                    )
                    if nature_.Name == "Pneu":
                        pneu_achat = Pneu.objects.get(Numero=numero_saisie, Marque=marque_saisie, Details__icontains=details)
                        PneuHistorique.objects.create(
                            Pneu_Numero=pneu_achat,
                            Historique_idHistorique=history
                        )
                    elif nature_.Name == "Batterie":
                        batterie_achat = Batterie.objects.get(Numero=numero_saisie, Marque=marque_saisie, Details__icontains=details)
                        BatterieHistorique.objects.create(
                            Batterie_Numero=batterie_achat,
                            Historique_idHistorique=history
                        )
                    else:
                        accessoire_achat = Accessoire.objects.get(Numero=numero_saisie, Marque=marque_saisie,
                                                              Details__icontains=details)
                        AccessoireHistorique.objects.create(
                            Accesoire_Numero=accessoire_achat,
                            Historique_idHistorique=history
                        )
            return redirect("myapp:historique", client_id=client.idClient)
        else:
            marques = Marque.objects.all()
            context = {
                "marques": marques
            }
            return render(request, template_name="sortie.html", context=context)


def get_marques(request):
    marques = [marque.Nom for marque in Marque.objects.all()]
    return JsonResponse({"marques": marques})


def get_natures(request):
    natures = [nature.Name for nature in Nature.objects.all()]
    return JsonResponse({"natures": natures})


def entre(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    if admin is not None:
        if request.method == "GET":
            marque = request.GET.get("ajout")
            if marque is not None:
                if Marque.objects.filter(Nom=marque).exists():
                    message = "MARQUE DEJA AJOUTE !!"
                    context = {
                        "message": message
                    }
                    return render(request, "entre.html", context)
                Marque.objects.create(
                    Nom=marque
                )
                return redirect("myapp:entre")
        elif request.method == "POST":
            nombre_de_lignes = int(request.POST.get('nombre_de_lignes'))
            date = request.POST.get("date")
            nom_fournisseur = request.POST.get("nom_fournisseur")
            contact_fournisseur = request.POST.get("contact_fournisseur")
            for i in range(1, nombre_de_lignes + 1):
                marque = request.POST.get(f'marque_{i}')
                numero_saisie = request.POST.get(f'numero_{i}')
                details = request.POST.get(f'details_{i}')
                nature = request.POST.get(f'nature_{i}')
                if details is None:
                    details = ""
                prix = float(request.POST.get(f'prix_{i}'))
                stockage = request.POST.get(f'stockage_{i}')
                quantite = int(request.POST.get(f'quantite_{i}'))

                if Marque.objects.filter(Nom=marque).exists() and Nature.objects.filter(Name=nature).exists():
                    marque_ = Marque.objects.get(Nom=marque)
                    nature_ = Nature.objects.get(Name=nature)
                    try:
                        fournisseur = Fournisseur.objects.get(Contact=contact_fournisseur)
                    except Fournisseur.DoesNotExist:
                        fournisseur = Fournisseur.objects.create(
                            Nom=nom_fournisseur,
                            Contact=contact_fournisseur
                        )
                    try:
                        numero = Numero.objects.get(Numero=numero_saisie)
                        if numero is not None:
                            if nature_.Name == "Pneu":
                                try:
                                    pneu = Pneu.objects.get(Numero=numero, Marque=marque_, Details=details)
                                    if pneu is not None:
                                        pneu.Quantite += quantite
                                        pneu.Date = date
                                        pneu.Prix = prix
                                        pneu.Stockage = stockage
                                        pneu.Fournisseur = fournisseur
                                        pneu.save()
                                except Pneu.DoesNotExist:
                                    Pneu.objects.create(
                                        Numero=numero,
                                        Details=details,
                                        Prix=prix,
                                        Stockage=stockage,
                                        Quantite=quantite,
                                        Date=date,
                                        Fournisseur=fournisseur,
                                        Marque=marque_
                                    )
                            elif nature_.Name == "Batterie":
                                try:
                                    batterie = Batterie.objects.get(Numero=numero, Marque=marque_, Details=details)
                                    if batterie is not None:
                                        batterie.Quantite += quantite
                                        batterie.Date = date
                                        batterie.Prix = prix
                                        batterie.Stockage = stockage
                                        batterie.Fournisseur = fournisseur
                                        batterie.save()
                                except Batterie.DoesNotExist:
                                    Batterie.objects.create(
                                        Numero=numero,
                                        Details=details,
                                        Prix=prix,
                                        Stockage=stockage,
                                        Quantite=quantite,
                                        Date=date,
                                        Fournisseur=fournisseur,
                                        Marque=marque_
                                    )
                            else:
                                try:
                                    accessoire = Accessoire.objects.get(Numero=numero, Marque=marque_, Details=details)
                                    if accessoire is not None:
                                        accessoire.Quantite += quantite
                                        accessoire.Date = date
                                        accessoire.Prix = prix
                                        accessoire.Stockage = stockage
                                        accessoire.Fournisseur = fournisseur
                                        accessoire.save()
                                except Accessoire.DoesNotExist:
                                    Accessoire.objects.create(
                                        Numero=numero,
                                        Details=details,
                                        Prix=prix,
                                        Stockage=stockage,
                                        Quantite=quantite,
                                        Date=date,
                                        Fournisseur=fournisseur,
                                        Marque=marque_
                                    )
                    except Numero.DoesNotExist:
                        numero = Numero.objects.create(
                            Numero=numero_saisie,
                            Quantite=quantite
                        )
                        if nature_.Name == "Pneu":
                            Pneu.objects.create(
                                Numero=numero,
                                Details=details,
                                Prix=prix,
                                Stockage=stockage,
                                Quantite=quantite,
                                Date=date,
                                Fournisseur=fournisseur,
                                Marque=marque_
                            )
                        elif nature_.Name == "Batterie":
                            Batterie.objects.create(
                                Numero=numero,
                                Details=details,
                                Prix=prix,
                                Stockage=stockage,
                                Quantite=quantite,
                                Date=date,
                                Fournisseur=fournisseur,
                                Marque=marque_
                            )
                        else:
                            Accessoire.objects.create(
                                Numero=numero,
                                Details=details,
                                Prix=prix,
                                Stockage=stockage,
                                Quantite=quantite,
                                Date=date,
                                Fournisseur=fournisseur,
                                Marque=marque_
                            )
                    Transaction.objects.create(
                        Numero=numero,
                        Details=details,
                        Prix=prix,
                        Stockage=stockage,
                        Quantite=quantite,
                        Date=date,
                        Fournisseur=fournisseur,
                        Marque=marque_,
                        Nature=nature_
                    )
                    marque_saisie = Marque.objects.get(Nom=marque)
                    marque_saisie.Quantite += quantite
                    marque_saisie.save()
                    numero_saisie.Quantite += quantite
                    numero_saisie.save()
                else:
                    return redirect("myapp:stock")
            return redirect("myapp:stock")

        else:
            marques = Marque.objects.all()
            if marques is None:
                marques = []
            context = {
                "marques": marques
            }
            return render(request, "entre.html", context=context)
    return render(request, "entre.html")


def transaction(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    if admin is not None:
        if request.method == "POST":
            marque = request.POST.get("marque")
            try:
                marque_saisie = Marque.objects.get(Nom=marque)
            except Marque.DoesNotExist:
                marque = "All"
                marque_saisie = "All"
            nature = request.POST.get("nature")
            try:
                nature_saisie = Nature.objects.get(Name=nature)
            except Nature.DoesNotExist:
                nature = "All"
                nature_saisie = "All"
            numero = request.POST.get("numero")
            if numero is None:
                numero = ""
                numero_saisi = None
            else:
                try:
                    numero_saisi = Numero.objects.get(Numero=numero)
                except Numero.DoesNotExist:
                    numero_saisi = None
            recherche = f"{marque} - {numero}"
            if recherche:
                if marque != "All" and nature != 'All':
                    if numero_saisi is None:
                        resultat = Transaction.objects.filter(Marque=marque_saisie).order_by("-Date")
                    else:
                        resultat = Transaction.objects.filter(Marque=marque_saisie, Numero=numero_saisi).order_by("-Date")
                elif marque != "All" and nature == "All":
                    if numero_saisi is None:
                        resultat = Transaction.objects.filter(Marque=marque_saisie).order_by("-Date")
                    else:
                        resultat = Transaction.objects.filter(Marque=marque_saisie, Numero=numero_saisi).order_by("-Date")
                elif marque == "All" and nature != "All":
                    if numero_saisi is None:
                        resultat = Transaction.objects.filter(Nature=nature_saisie).order_by("-Date")
                    else:
                        resultat = Transaction.objects.filter(Nature=nature_saisie, Numero=numero_saisi).order_by("-Date")
                else:
                    if numero_saisi is None:
                        resultat = Transaction.objects.all().order_by("-Date")
                    else:
                        resultat = Transaction.objects.filter(Numero=numero_saisi).order_by("-Date")

                if resultat.exists():
                    total_pneu = resultat.count()
                    somme_quantites = resultat.aggregate(Sum('Quantite'))['Quantite__sum'] or 1
                    nbre_pneu_marque = Marque.objects.values('Nom').annotate(nombre_pneus=Count('Nom'))
                    resultat = resultat.annotate(valeur_restante=ExpressionWrapper(F('Quantite') * F('Prix'), output_field=DecimalField()))
                    marques = Marque.objects.all()
                    natures = Nature.objects.all()
                    context = {
                        "transactions": resultat,
                        "total_pneu": total_pneu,
                        "total_stock": somme_quantites,
                        "nbre_pneus": nbre_pneu_marque,
                        "marques": marques,
                        "natures": natures,
                        "recherche": recherche
                    }
                    return render(request, "transaction.html", context=context)
                else:
                    marques = Marque.objects.all()
                    message = "AUCUN RESULTAT TROUVE !"
                    context = {
                        "message": message,
                        "marques": marques
                    }
                    return render(request, "transaction.html", context=context)
        else:
            pneus = Transaction.objects.all().order_by("-Date")
            somme_quantites = pneus.aggregate(Sum('Quantite'))['Quantite__sum'] or 1
            resultat = pneus.annotate(valeur_restante=ExpressionWrapper(F('Quantite') * F('Prix'), output_field=DecimalField()))
            marques = Marque.objects.all()
            natures = Nature.objects.all()
            context = {
                "transactions": resultat,
                "total_stock": somme_quantites,
                "marques": marques,
                "natures": natures
            }
            return render(request, "transaction.html", context=context)


def stock(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    if admin is not None:
        if request.method == "POST":
            marque = request.POST.get("marque")
            try:
                marque_saisie = Marque.objects.get(Nom=marque)
            except Marque.DoesNotExist:
                marque = "All"
                marque_saisie = "All"
            nature = request.POST.get("nature")
            try:
                nature_saisie = Nature.objects.get(Name=nature)
            except Nature.DoesNotExist:
                nature = "All"
                nature_saisie = "All"
            numero = request.POST.get("numero")
            if numero is None:
                numero = ""
                numero_saisi = None
            else:
                try:
                    numero_saisi = Numero.objects.get(Numero=numero)
                except Numero.DoesNotExist:
                    numero_saisi = None
            recherche = f"{marque} - {numero}"
            batteries = None
            pneus = None
            accessoires = None
            if recherche:
                if marque != "All" and nature != "All":
                    if numero_saisi is None:
                        if nature_saisie.Name == "Pneu":
                            pneus = Pneu.objects.filter(Marque=marque_saisie).order_by("-idPneu")
                        elif nature_saisie.Name == "Batterie":
                            batteries = Batterie.objects.filter(Marque=marque_saisie).order_by("-idBatterie")
                        else:
                            accessoires = Accessoire.objects.filter(Marque=marque_saisie).order_by("-idAccessoire")
                    else:
                        if nature_saisie.Name == "Pneu":
                            pneus = Pneu.objects.filter(Marque=marque_saisie, Numero=numero_saisi).order_by("-idPneu")
                        elif nature_saisie.Name == "Batterie":
                            batteries = Batterie.objects.filter(Marque=marque_saisie, Numero=numero_saisi).order_by("-idBatterie")
                        else:
                            accessoires = Accessoire.objects.filter(Marque=marque_saisie, Numero=numero_saisi).order_by("-idAccessoire")
                elif nature != "All" and marque == "All":
                    if numero_saisi is None:
                        if nature_saisie.Name == "Pneu":
                            pneus = Pneu.objects.all().order_by("-idPneu")
                        elif nature_saisie.Name == "Batterie":
                            batteries = Batterie.objects.all().order_by("-idBatterie")
                        else:
                            accessoires = Accessoire.objects.all().order_by("-idAccessoire")
                    else:
                        if nature_saisie.Name == "Pneu":
                            pneus = Pneu.objects.filter(Numero=numero_saisi).order_by("-idPneu")
                        elif nature_saisie.Name == "Batterie":
                            batteries = Batterie.objects.filter(Numero=numero_saisi).order_by("-idBatterie")
                        else:
                            accessoires = Accessoire.objects.filter(Numero=numero_saisi).order_by("-idAccessoire")
                elif nature == "All" and marque != "All":
                    if numero_saisi is None:
                        pneus = Pneu.objects.filter(Marque=marque_saisie).order_by("-idPneu")
                        batteries = Batterie.objects.filter(Marque=marque_saisie).order_by("-idBatterie")
                        accessoires = Accessoire.objects.filter(Marque=marque_saisie).order_by("-idAccessoire")
                    else:
                        pneus = Pneu.objects.filter(Marque=marque_saisie, Numero=numero_saisi).order_by("-idPneu")
                        batteries = Batterie.objects.filter(Marque=marque_saisie, Numero=numero_saisi).order_by("-idBatterie")
                        accessoires = Accessoire.objects.filter(Marque=marque_saisie, Numero=numero_saisi).order_by("-idAccessoire")
                else:
                    if numero_saisi is None:
                        pneus = Pneu.objects.all()
                        batteries = Batterie.objects.all()
                        accessoires = Accessoire.objects.all()
                    else:
                        pneus = Pneu.objects.filter(Numero=numero_saisi)
                        batteries = Batterie.objects.filter(Numero=numero_saisi)
                        accessoires = Accessoire.objects.filter(Numero=numero_saisi)

                if pneus is not None or batteries is not None or accessoires is not None:
                    # somme_quantites = resultat.aggregate(Sum('Quantite'))['Quantite__sum'] or 1
                    if pneus is not None:
                        pneus = pneus.annotate(valeur_restante=ExpressionWrapper(F('Quantite') * F('Prix'), output_field=DecimalField()))
                    if batteries is not None:
                        batteries = batteries.annotate(valeur_restante=ExpressionWrapper(F('Quantite') * F('Prix'), output_field=DecimalField()))
                    if accessoires is not None:
                        accessoires = accessoires.annotate(valeur_restante=ExpressionWrapper(F('Quantite') * F('Prix'), output_field=DecimalField()))
                    marques = Marque.objects.all()
                    natures = Nature.objects.all()
                    context = {
                        "pneus": pneus,
                        "accessoires": accessoires,
                        "batteries": batteries,
                        "natures": natures,
                        "marques": marques,
                    }
                    return render(request, "stock.html", context=context)
        else:
            natures = Nature.objects.all()
            marques = Marque.objects.all()
            pneus = Pneu.objects.all()
            pneus = pneus.annotate(valeur_restante=ExpressionWrapper(F('Quantite') * F('Prix'), output_field=DecimalField()))
            batteries = Batterie.objects.all()
            batteries = batteries.annotate(valeur_restante=ExpressionWrapper(F('Quantite') * F('Prix'), output_field=DecimalField()))
            accessoires = Accessoire.objects.all()
            accessoires = accessoires.annotate(valeur_restante=ExpressionWrapper(F('Quantite') * F('Prix'), output_field=DecimalField()))
            context = {
                "natures": natures,
                "pneus": pneus,
                "batteries": batteries,
                "accessoires": accessoires,
                "marques": marques
            }
            return render(request, "stock.html", context=context)



def list_client(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    if admin is not None:
        if request.method == "POST":
            search_bar = request.POST.get("search")
            if search_bar:
                resultat = Client.objects.filter(
                    Nom__icontains=search_bar) | Client.objects.filter(
                    Nom__startswith=search_bar) | Client.objects.filter(
                    Contact__startswith=search_bar) | Client.objects.filter(Statut__icontains=search_bar)

                montant_total_restant = 0
                for client in resultat:
                    if (client.montant_restant() - client.montant_paye_history()) >= 0:
                        montant_total_restant += (client.montant_restant() - client.montant_paye_history())
                context = {
                    "clients": resultat,
                    "montant_credt": montant_total_restant
                }
                return render(request, "listclient.html", context)
        else:
            list_client = Client.objects.all().order_by("-idClient")
            montant_total_restant = 0
            for client in list_client:
                if (client.montant_restant() - client.montant_paye_history()) >= 0:
                    montant_total_restant += (client.montant_restant() - client.montant_paye_history())
            context = {
                "clients": list_client,
                "montant_credt": montant_total_restant
            }
            return render(request, "listclient.html", context)


def list_fournisseur(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    if admin is not None:
        if request.method == "POST":
            search_bar = request.POST.get("search")
            if search_bar:
                resultat = Fournisseur.objects.filter(
                    Nom__icontains=search_bar) | Fournisseur.objects.filter(
                    Nom__startswith=search_bar) | Fournisseur.objects.filter(
                    Contact__startswith=search_bar) | Fournisseur.objects.filter(Statut__icontains=search_bar)

                context = {
                    "fournisseurs": resultat
                }
                return render(request, "listfournisseur.html", context)
        else:
            list_fourniss = Fournisseur.objects.all().order_by("-idFournisseur")
            context = {
                "fournisseurs": list_fourniss
            }
            return render(request, "listfournisseur.html", context)


def historique(request, client_id):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    if admin is not None:
        client = Client.objects.get(pk=client_id)
        if client is not None:
            if request.method == "POST":
                date = request.POST.get("date")
                motif = request.POST.get("motif")
                montant = int(request.POST.get("montant"))
                if date and motif and montant:
                    montant_total_restant = client.montant_restant() - client.montant_paye_history()
                    montant_restant = int(montant_total_restant - decimal.Decimal(str(montant)))
                    Historique.objects.create(
                        Date_Achat=date,
                        Designation=motif,
                        Montant_Total=client.montant_restant() - client.montant_paye_history(),
                        Montant_Paye=montant,
                        Montant_Restant=montant_restant,
                        Client=client
                    )
                    if montant_restant <= 0:
                        client.Statut = True
                        client.save()
                    else:
                        client.Statut = False
                        client.save()
                    return redirect("myapp:historique", client_id=client.idClient)
            else:
                montant_restant = client.montant_restant() - client.montant_paye_history()
                montant_paye = client.montant_paye()
                montant_total = client.montant_total()
                list_historique = Historique.objects.filter(Client=client).order_by("-idHistorique")
                context = {
                    "historiques": list_historique,
                    "client": client,
                    "montant_achat": montant_total,
                    "montant_credit": montant_restant,
                    "montant_versement": montant_paye
                }
                return render(request, "historique.html", context)


def achat(request, client_id):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    try:
        client = Client.objects.get(pk=client_id)
    except:
        return redirect("myapp:list_client")
    if admin is not None:
        if request.method == "POST":
            nombre_lignes = int(request.POST.get("nombre_de_lignes"))
            date = request.POST.get("date")
            montant_paye_total = float(request.POST.get("montant_paye"))
            montant_total_precedent = 0
            montant_restant_precedent = 0
            for i in range(1, nombre_lignes + 1):
                marque = request.POST.get(f"marque_{i}")
                numero = request.POST.get(f"numero_{i}")
                try:
                    numero_ = Numero.objects.get(Numero=numero)
                except Numero.DoesNotExist:
                    message = "Le Numero n'existe pas !!"
                    return render(request, achat.html, {"message": message})
                nature = request.POST.get(f"nature_{i}")
                details = request.POST.get(f"details_{i}")
                if details is None:
                    details = ""
                prix = float(request.POST.get(f"prix_{i}"))
                quantite = int(request.POST.get(f"quantite_{i}"))
                montant_total = float(prix * quantite)
                if i > 1:
                    if montant_restant_precedent > 0:
                        montant_paye_total = 0
                    else:
                        montant_paye_total -= montant_total_precedent
                    montant_restant = float(montant_total - montant_paye_total)
                    if montant_restant > 0:
                        client.Statut = False
                        client.save()
                    else:
                        client.Statut = True
                        client.save()
                else:
                    montant_restant = float(montant_total - montant_paye_total)
                    if montant_restant > 0:
                        client.Statut = False
                        client.save()
                    else:
                        client.Statut = True
                        client.save()
                montant_restant_precedent = montant_restant
                montant_total_precedent = montant_total
                designation = f"{marque} {numero} {details}"
                marque_saisie = Marque.objects.get(Nom=marque)
                quantite_marque = marque_saisie.Quantite - quantite
                nature_ = Nature.objects.get(Name=nature)
                numero_saisie = Numero.objects.get(Numero=numero)
                quantite_numero = numero_saisie.Quantite - quantite
                if (quantite_marque < 0 or marque_saisie.Quantite == 0) and (quantite_numero < 0 or numero_saisie.Quantite == 0):
                    message = "Quantité insuffisant !!"
                    context = {
                        "quantite_null": message
                    }
                    return render(request, "achat.html", context=context)
                else:
                    if nature_.Name == "Pneu":
                        try:
                            pneu = Pneu.objects.get(Marque=marque_saisie, Numero=numero_saisie, Details__icontains=details)
                        except Pneu.DoesNotExist:
                            message = "Pneu non existant"
                            context = {"error_pneu": message}
                            return render(request, "achat.html", context)
                        if pneu is not None:
                            if pneu.Quantite <= 0 or pneu.Quantite < quantite:
                                message = f"Quantité de pneu insuffisant ! Il reste {pneu.Quantite} pneu(s)"
                                context = {"error_pneu": message}
                                return render(request, "achat.html", context)
                            else:
                                pneu.Quantite -= quantite
                                pneu.save()
                    elif nature_.Name == "Batterie":
                        try:
                            batterie = Batterie.objects.get(Marque=marque_saisie, Numero=numero_saisie, Details__icontains=details)
                        except Batterie.DoesNotExist:
                            message = "Batterie non existant"
                            context = {"error_pneu": message}
                            return render(request, "achat.html", context)
                        if batterie is not None:
                            if batterie.Quantite <= 0 or batterie.Quantite  < quantite:
                                message = f"Quantité de batterie insuffisant ! Il reste {batterie.Quantite} batterie(s)"
                                context = {"error_pneu": message}
                                return render(request, "achat.html", context)
                            else:
                                batterie.Quantite -= quantite
                                batterie.save()
                    else:
                        try:
                            accessoire = Accessoire.objects.get(Marque=marque_saisie, Numero=numero_saisie, Details__icontains=details)
                        except Accessoire.DoesNotExist:
                            message = "Accessoire non existant"
                            context = {"error_pneu": message}
                            return render(request, "achat.html", context)
                        if accessoire is not None:
                            if accessoire.Quantite <= 0 or accessoire.Quantite  < quantite:
                                message = f"Quantité d'accessoire insuffisant ! Il reste {accessoire.Quantite} accessoire(s)"
                                context = {"error_pneu": message}
                                return render(request, "achat.html", context)
                            else:
                                accessoire.Quantite -= quantite
                                accessoire.save()
                    marque_saisie.Quantite = quantite_marque
                    marque_saisie.save()
                    numero_saisie.Quantite = quantite_numero
                    numero_saisie.save()
                history = Historique.objects.create(
                    Date_Achat=date,
                    Designation=designation,
                    Montant_Total=montant_total,
                    Montant_Paye=montant_paye_total,
                    Montant_Restant=montant_restant,
                    Client=client
                )
                if nature_.Name == "Pneu":
                    pneu_achat = Pneu.objects.get(Numero=numero_saisie, Marque=marque_saisie, Details__icontains=details)
                    PneuHistorique.objects.create(
                        Pneu_Numero=pneu_achat,
                        Historique_idHistorique=history
                    )
                elif nature_.Name == "Batterie":
                    batterie_achat = Batterie.objects.get(Numero=numero_saisie, Marque=marque_saisie, Details__icontains=details)
                    BatterieHistorique.objects.create(
                        Batterie_Numero = batterie_achat,
                        Historique_idHistorique=history
                    )
                else:
                    accessoire_achat = Accessoire.objects.get(Numero=numero_saisie, Marque=marque_saisie, Details__icontains=details)
                    AccessoireHistorique.objects.create(
                        Accesoire_Numero = accessoire_achat,
                        Historique_idHistorique=history
                    )
            return redirect("myapp:historique", client_id=client.idClient)
        else:
            marques = Marque.objects.all()
            context = {
                "client": client,
                "marques": marques
            }
            return render(request, template_name="achat.html", context=context)


def credit(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion")
    if admin is not None:
        if request.method == "POST":
            search_bar = request.POST.get("search")
            if search_bar:
                resultat = Client.objects.filter(
                    Nom__icontains=search_bar) & Client.objects.filter(Statut=False) | Client.objects.filter(
                    Nom__startswith=search_bar) & Client.objects.filter(Statut=False) | Client.objects.filter(
                    Contact__startswith=search_bar) & Client.objects.filter(Statut=False)
                montant_total_restant = 0
                for client in resultat:
                    if (client.montant_restant() - client.montant_paye_history()) >= 0:
                        montant_total_restant += (client.montant_restant() - client.montant_paye_history())
                context = {
                    "clients": resultat,
                    "montant_credt": montant_total_restant
                }
                return render(request, "credit.html", context)
        else:
            list_client = Client.objects.filter(Statut=0).order_by("-idClient")
            montant_total_restant = 0
            for client in list_client:
                if (client.montant_restant() - client.montant_paye_history()) >= 0:
                    montant_total_restant += (client.montant_restant() - client.montant_paye_history())
            context = {
                "clients": list_client,
                "montant_credt": montant_total_restant
            }
            return render(request, "credit.html", context)


def connexion(request):
    if request.method == "POST":
        password = request.POST.get("Password")
        admin = Administrateur.objects.get(idAdministrateur=1)
        if password == admin.Password:
            request.session["admin_id"] = admin.idAdministrateur
            return redirect("myapp:stock")
        else:
            message = "MOT DE PASSE INCORRECT !!!!"
            context = {
                "message": message
            }
            return render(request, "connexion.html", context)
    return render(request, "connexion.html")
