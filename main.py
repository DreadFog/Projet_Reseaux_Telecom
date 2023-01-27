import argparse
import random
from statistics import mean
from Commutateur import Commutateur, Strategie, printv, CTS_count, CA_count, printStrategy, traffic_state
from User import User
from typing import List
import matplotlib.pyplot as plt
#import networkx as nx
#import numpy as np
from itertools import  filterfalse

isVerbose = False
users_count = 0
MOYENNE = 1#5
PCT_MAX = 1#9
# capacity of the links
cts_wire = 5
cts_ca_wire = 2
ca_wire = 1
# Création des pannes: première méthode
# idée: on choisit un commutateur, on choisit un de ses voisins, on supprime le lien
def generer_pannes_1(nbPanne, commutateurs, pannesCrees):
    for _ in range(nbPanne):
        # choisir un commutateur non isolé
        comPanneExt1 = commutateurs[random.randint(0,len(commutateurs)-1)]
        while len(comPanneExt1.voisins) == 0:
            comPanneExt1 = commutateurs[random.randint(0,len(commutateurs)-1)]
        adsVoisins = list(comPanneExt1.voisins.keys())
        # choisir un de ses voisins
        comPanneExt2 = comPanneExt1.voisins[adsVoisins[random.randint(0,len(adsVoisins)-1)]][2]
        capacite = comPanneExt1.supprimerVoisin(comPanneExt2)
        comPanneExt2.supprimerVoisin(comPanneExt1)
        # mémorisation de la panne
        pannesCrees.append((comPanneExt1, comPanneExt2, capacite))
        pannesCrees.append((comPanneExt2, comPanneExt1, capacite))

# Rétablissement des pannes provoquées par la méthode 1
def fix_pannes_1(pannesCrees):
        for (comPanneExt1, comPanneExt2, capacite) in pannesCrees:
            comPanneExt1.ajouterVoisin(comPanneExt2, capacite)

# création des pannes: deuxième méthode
# idée: on remplit les liens plutot que de les supprimer
def generer_pannes_2(nbPanne, commutateurs, pannesCrees):
    for _ in range(nbPanne):
        # choisir un commutateur non isolé
        comPanneExt1 = commutateurs[random.randint(0,len(commutateurs)-1)]
        while len(comPanneExt1.voisins) == 0:
            comPanneExt1 = commutateurs[random.randint(0,len(commutateurs)-1)]
        adsVoisins = list(comPanneExt1.voisins.keys())
        # choisir un de ses voisins
        voisinChoisi = adsVoisins[random.randint(0,len(adsVoisins)-1)]
        (commsEnCours1, capa, comPanneExt2) = comPanneExt1.voisins[voisinChoisi]
        (commsEnCours2, capa, _)            = comPanneExt2.voisins[comPanneExt1.adresse]
        # remplir le lien au maximum de sa capacité
        for i in range(capa):
            commsEnCours1.append((-(i+1), i, i)) # adresse factice négative
            commsEnCours2.append((-(i+1), i, i))
        # mémorisation de la panne
        pannesCrees.append((comPanneExt1, _, voisinChoisi))
        pannesCrees.append((comPanneExt2, _, comPanneExt1.adresse))
        printv(f"Panne entre {comPanneExt1} et {comPanneExt2}", isVerbose)

# création de pannes: troisième méthode
# idée: on remplit tous les liens des commutateurs choisis
def generer_pannes_3(nbPanne, commutateurs, pannesCrees):
    for _ in range(nbPanne):
        # choisir un commutateur non isolé
        comPanneExt1 = commutateurs[random.randint(0,len(commutateurs)-1)]
        while len(comPanneExt1.voisins) == 0:
            comPanneExt1 = commutateurs[random.randint(0,len(commutateurs)-1)]
        adsVoisins = list(comPanneExt1.voisins.keys())
        # parcourir les voisins
        for v in adsVoisins:
            (commsEnCours1, capa, comPanneExt2) = comPanneExt1.voisins[v]
            (commsEnCours2, _, _) = comPanneExt2.voisins[comPanneExt1.adresse]
            # remplir le lien au maximum de sa capacité
            for i in range(capa):
                commsEnCours1.append((-(i+1), i, i)) # adresse factice négative
                commsEnCours2.append((-(i+1), i, i)) # adresse factice négative
            # mémorisation de la panne
            pannesCrees.append((comPanneExt1, _, v))

# Rétablissement des pannes provoquées par les méthodes 2 et 3
def fix_pannes_2_3(pannesCrees):
    for (comPanneExt1, _, voisinChoisi) in pannesCrees:
        comPanneExt1.voisins[voisinChoisi][0].clear()

def essai_appel(users, liste_clients_appelants):
        """Simulation des appels entre clients"""
        # Choix de la source et de la destination
        l_clients_appel_BAR = list(filterfalse(lambda x: x in liste_clients_appelants, users))
        client_source = l_clients_appel_BAR[random.randint(0, len(l_clients_appel_BAR)-1)]
        # while client_source in liste_clients_appelants:
        #     client_source = users[random.randint(0, len(users)-1)]

        client_dest = users[random.randint(0, len(users)-1)]
        # Eviter qu'un client s'appelle lui-même
        while (client_dest == client_source):
            client_dest = users[random.randint(0, len(users)-1)]

        printv(f"Appel de {client_source.adresse} vers {client_dest.adresse}", isVerbose)
        return client_source, client_source.appel(client_dest.adresse, isVerbose)


def getChargeRefus(users, nbRefusInitial, nbPanne, commutateurs):
        resultats = (list(), list(), list())
        printv(f"Nombre de pannes : {nbPanne}", isVerbose)
        # Pour une charge réseau de 10% à 90%, par pas de 10%, on mesure le taux t'appels refusés
        for i in range(1,PCT_MAX+1):
            print(f"Charge du réseau : {i*10}%" )
            charge_reseau_max = i * (users_count // 10 if users_count >= 10 else 1)

            liste_clients_appelants : List[User] = list()

            nb_appels_acceptes = 0
            nb_appels_refuses = 0

            for _ in range(MOYENNE):
                pannesCrees = list()
                # On créé les pannes
                #generer_pannes_1(nbPanne, commutateurs, pannesCrees)
                generer_pannes_2(nbPanne, commutateurs, pannesCrees)
                #generer_pannes_3(nbPanne, commutateurs, pannesCrees)

                # On "remplit" le réseau avant de commencer à mesurer le taux d'appels refusés
                while(len(liste_clients_appelants) < charge_reseau_max) :
                    printv(f"{len(liste_clients_appelants)} / {charge_reseau_max}, users : {len(users)}, users_count : {users_count}", isVerbose)
                    source, appel_reussi = essai_appel(users, liste_clients_appelants)
                    if appel_reussi:
                        liste_clients_appelants.append(source)

                for _ in range(charge_reseau_max): # facteur moyenner suffisamment longtemps

                    # print(f"Appels en cours : {liste_clients_appelants}")

                    # S'il y a trop d'appels en cours, on ferme le premier de la liste
                    if len(liste_clients_appelants) >= charge_reseau_max:
                        liste_clients_appelants[0].raccrocher(isVerbose)
                        liste_clients_appelants.pop(0)

                    client_source, appel_reussi = essai_appel(users, liste_clients_appelants)

                    if appel_reussi:
                        liste_clients_appelants.append(client_source)
                        nb_appels_acceptes += 1
                    else:
                        nb_appels_refuses += 1

                # Tout le monde raccroche
                for client in liste_clients_appelants:
                    client.raccrocher(isVerbose)

                # On résout les pannes
                #fix_pannes_1(pannesCrees)
                fix_pannes_2_3(pannesCrees)

            resultats[0].append(i/10)
            resultats[1].append(nb_appels_refuses / (nb_appels_acceptes + nb_appels_refuses) * 100)
            resultats[2].append(nb_appels_refuses-nbRefusInitial[i-1])

        return resultats

if __name__ == "__main__":
    ####### PARSING #######
    parser = argparse.ArgumentParser(
                    prog = 'RouteComparer',
                    description = 'Program evaluating and comparing the performance of different routing algorithms',
                    epilog = 'Project for ENSEEIHT, 2023')
    parser.add_argument('-s', '--strategie',
                        help="strategy used between Statique, PartageCharge and Adaptative",
                        choices=['Statique', 'PartageCharge', 'Adaptative', 'Dijkstra'],
                        dest='strategy',
                        default="Statique")
    parser.add_argument('-n', '--number_of_users', dest='nc')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False)
    args = vars(parser.parse_args())
    s = args.get('strategy')
    chosenStrategy : Strategie
    match s:
        case 'Statique':
            chosenStrategy = Strategie.Statique
        case 'PartageCharge':
            chosenStrategy = Strategie.PartageCharge
        case 'Adaptative':
            chosenStrategy = Strategie.Adaptative
        case 'Dijkstra':
            chosenStrategy = Strategie.Dijkstra
        case _:
            print("Error: unknown strategy. Defaulting to Statique")
            chosenStrategy = Strategie.Statique
    #printv("Strategy chosen : " + str(chosenStrategy).split('.')[1], isVerbose)
    isVerbose = bool(args.get('verbose'))
    arg_nc = args.get('nc')
    users_count : int = int(arg_nc) if (arg_nc != None) else 100 # nombre de users par défaut
    assert(users_count > PCT_MAX)

    ####### INIT #######
    users_per_CA = users_count // CA_count
    printv("Users per CA: {}".format(users_per_CA), isVerbose)
    # when parsing is ok, create the network, and a list of users
    #           1.0.0                  2.0.0                  3.0.0
    #           CTS1-------------------CTS2-------------------CTS3
    #            /\ \                   /\                     /\
    #           /  \  \                /  \
    #          /    \                 /    \
    #         /      \               /      \
    #        |        \             /        \
    #        |         \           /          \               ...
    #        |          \         /            \
    #        |           \       /              \            
    #        |            \      |               \
    #        |             \     |                \
    #        |              \    |                 \
    #        |               \   |                  |
    #      1.1.0              \1.2.0               2.3.0                3.4.0
    #       CA1-----------------CA2-----------------CA3-----------------CA4      
    #        |                   |                   |                    |
    #        |                   |                   |                    |
    #        |                   |                   |                    |
    #    c[0]-c[n/4-1]     c[n/4]-c[n/2-1]      c[n/2]-c[3n/4-1]     c[3n/4]-c[n]
    adresses_CTS = range(1, CTS_count+1)
    adresses_CA = range(1, CA_count+1)

    liste_CA: list[Commutateur] = list()
    liste_CTS: list[Commutateur] = list()

    for i in adresses_CTS:
        printv((i,0,0), isVerbose)
        liste_CTS.append(Commutateur((i,0,0), chosenStrategy))

    for i in adresses_CA:
        # choice: address prefix of a CA is the same as the CTS of same idx. Ex: CA1 and CTS1 have same prefix
        liste_CA.append(Commutateur((int(i*CTS_count/CA_count+(1 if i==1 else 0)),i,0), chosenStrategy))

    # Interconnection of the CTS
    # Edge cases: first and last ones are only connected to one of their kind and two of the other kind
    lenCTS = len(liste_CTS)
    lenCA = len(liste_CA)

    # Edge cases
    liste_CTS[0].ajouterVoisins([ (liste_CTS[1], cts_wire)
                                , (liste_CA[0], cts_ca_wire)
                                , (liste_CA[1], cts_ca_wire)])
    liste_CTS[-1].ajouterVoisins([(liste_CTS[-2], cts_wire)
                                 , (liste_CA[-1], cts_ca_wire)
                                 , (liste_CA[-2], cts_ca_wire)])
    # for CA
    liste_CA[0].ajouterVoisins([ (liste_CA[1], ca_wire)
                               , (liste_CTS[0], cts_ca_wire)
                               , (liste_CTS[1], cts_ca_wire)])
    liste_CTS[1].ajouterVoisin(liste_CA[0], cts_ca_wire)
    liste_CA[-1].ajouterVoisin(liste_CA[-2], ca_wire)

    # Connections between CTS
    for i in range(1, lenCTS -1): # omit first and last
        liste_CTS[i].ajouterVoisins([ (liste_CTS[i-1], cts_wire) # connected to 2 CTS
                                    , (liste_CTS[i+1], cts_wire)])

    # Connection between CAs
    for i in range(1, lenCA -1): # omit first and last
        liste_CA[i].ajouterVoisins([ (liste_CA[i-1], ca_wire) # connected to 2 CA
                                   , (liste_CA[i+1], ca_wire)])
    assert (lenCA >= lenCTS)
    # Cross 'Commutateurs' links
    for i in range(1, lenCA):
        liste_CA[i].ajouterVoisins([ (liste_CTS[int(i*CTS_count/CA_count+(1 if i==1 else 0))-1], cts_ca_wire)
                                   , (liste_CTS[int(i*CTS_count/CA_count+(1 if i==1 else 0))], cts_ca_wire)
                                   , (liste_CTS[int(i*CTS_count/CA_count+(1 if i==1 and i!=lenCTS-1 else 0)+(1 if i<lenCTS else 0))
                                   ], cts_ca_wire)])
        liste_CTS[int(i*CTS_count/CA_count+(1 if i==1 else 0))-1].ajouterVoisin(liste_CA[i], cts_ca_wire)
        liste_CTS[int(i*CTS_count/CA_count+(1 if i==1 else 0))].ajouterVoisin(liste_CA[i], cts_ca_wire)
        liste_CTS[int(i*CTS_count/CA_count+(1 if i==1 and i!=lenCTS-1 else 0))+(1 if i<lenCTS else 0)].ajouterVoisin(liste_CA[i], cts_ca_wire)

    if isVerbose:
        print("-------CTSs-------")
        for c in liste_CTS:
            print(f"CTS : {c.adresse}")
            print(*c.voisins)
        print("-------CAs-------")
        for c in liste_CA:
            print(f"CA : {c.adresse}")
            print(*c.voisins)

    resultats = dict()

    # create the users
    # It is a list of list of users. Each list of users is a group of users connected to the same CA
    liste_users : List[List[User]] = list()
    for c in liste_CA:
        liste_users.append(list())
        for i in range(0, users_per_CA):
            user_adress = tuple(list(c.adresse[0:-1]) + [i+1])
            printv(f"user : {user_adress} - CA : {c.adresse}", isVerbose)
            liste_users[-1].append(User(c, user_adress))
    printv(liste_users, isVerbose)
    flatten = lambda l: [] if l == [] else l[0] if len(l)==1 else l[0]+flatten(l[1:])
    flattened_list_user : List[User] = flatten(liste_users)
    printv(traffic_state, isVerbose)

    plots = plt.subplots(1,2)[1]
    """ plt.figure() """

    diffPannes = [0]*len(Strategie)
    nbRefusInitial = [0]*10
    commutateurs = liste_CA+liste_CTS
    countLinks = 0
    for c in commutateurs:
        countLinks += len(c.voisins)
    countLinks //= 2

    printv(f"Nombre de pannes : {countLinks}")
    nbPannes = int (0.20*countLinks)

    # Provoquer des pannes sur les liens
    for nbPanne in [0,nbPannes]: # Juste 5 pannes
        pannesCrees = list()

        # Faire varier la stratégie
        for strategy in [Strategie.PartageCharge]:#list(Strategie):
            label = printStrategy(strategy) + "" if nbPanne == 0 else " avec " + str(nbPanne) + " pannes"
            printv(f"Strategie : {printStrategy(strategy)}", isVerbose)

            for commutateur in liste_CTS:
                commutateur.setStrategy(strategy)
            for commutateur in liste_CA:
                commutateur.setStrategy(strategy)

            charge, tauxRefus, diff = getChargeRefus(flattened_list_user, nbRefusInitial, nbPanne, commutateurs)

            if nbPanne == 0:
                plots[0].plot(charge, tauxRefus, label=label)
                #plt.plot(charge, tauxRefus, label=label)
                nbRefusInitial = diff
            else:
                diffPannes[strategy.value] = mean(diff)/MOYENNE


    for strategy in list(Strategie):
        plots[1].bar(list(map(lambda s: printStrategy(s), Strategie)), diffPannes)

    plots[0].set(xlabel="Charge in %", ylabel = "Refused call rate in %")
    plots[1].set(xlabel = "Strategy", ylabel="Increase of refused calls")
    plots[0].set_title("Evolution of refused call rate")
    plots[1].set_title(f"Average increase in refused calls for {nbPannes} failures")
    plots[0].legend()
    plots[1].legend()
    """ plt.xlabel("Load in %")
    plt.ylabel("Refused call rate in %")
    plt.title("Evolution of refused call rate") 
    plt.legend()"""
    plt.show() 


else:
    print("Please run this script directly, not as a module.")