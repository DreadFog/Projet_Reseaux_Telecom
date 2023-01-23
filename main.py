import argparse
import random
from statistics import mean
from Commutateur import Commutateur, Strategie, printv, CTS_count, CA_count, printStrategy
from User import User
from typing import List
import matplotlib.pyplot as plt
from itertools import  filterfalse

isVerbose = False
users_count = 0
MOYENNE = 100#0

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


def getChargeRefus(users, nbRefusInitial):
        resultats = (list(), list(), list())

        # Pour une charge réseau de 10% à 90%, par pas de 10%, on mesure le taux t'appels refusés
        for i in range(1,6):
            print(f"Charge du réseau : {i*10}%" )
            charge_reseau_max = i * users_count // 10

            liste_clients_appelants : List[User] = list()

            nb_appels_acceptes = 0
            nb_appels_refuses = 0

            for _ in range(MOYENNE):
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

            resultats[0].append(i/10)
            resultats[1].append(nb_appels_refuses / (nb_appels_acceptes + nb_appels_refuses) * 100)
            resultats[2].append(nb_appels_refuses-nbRefusInitial[i-1])

            for client in liste_clients_appelants:
                client.raccrocher(isVerbose)

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
    print("Strategy chosen : " + str(chosenStrategy).split('.')[1])
    isVerbose = bool(args.get('verbose'))
    arg_nc = args.get('nc')
    users_count : int = int(arg_nc) if (arg_nc != None) else 100 # nombre de users par défaut

    ####### INIT #######
    # capacity of the links
    cts_wire = 50
    cts_ca_wire = 25
    ca_wire = 10
    users_per_CA = users_count // CA_count
    print("Users per CA: {}".format(users_per_CA))
    # when parsing is ok, create the network, and a list of users
    #           1.0.0                  2.0.0                  3.0.0
    #           CTS1-------------------CTS2-------------------CTS3
    #            /\                     /\                     /\
    #           /  \                   /  \
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
    #      1.1.0              \1.2.0               2.1.0
    #       CA1-----------------CA2-----------------CA3-----------------CA4      
    #        |                   |                   |                    |
    #        |                   |                   |                    |
    #        |                   |                   |                    |
    #    c[0]-c[n/4-1]     c[n/4]-c[n/2-1]      c[n/2]-c[3n/4-1]     c[3n/4]-c[n]
    # CTS : i.0.0 | CA int(i*nbCTS/nbCA).int(nbCTS/nbCA+1).0
    adresses_CTS = range(1, CTS_count)
    adresses_CA = range(1, CA_count)

    liste_CA: list[Commutateur] = list()
    liste_CTS: list[Commutateur] = list()

    for i in adresses_CTS:
        liste_CTS.append(Commutateur((i,0,0), chosenStrategy))

    for i in adresses_CA:
        # choice: address prefix of a CA is the same as the CTS of same idx. Ex: CA1 and CTS1 have same prefix
        print((int(i*CTS_count/CA_count+1),round(i+CTS_count/CA_count),0))
        liste_CA.append(Commutateur((int(i*CTS_count/CA_count+1),round(i+CTS_count/CA_count),0), chosenStrategy))

    #liste_CTS.insert(1, liste_CA.pop(-1))
    liste_CTS.insert(1, liste_CA.pop(-1))

    # Interconnection of the CTS
    # Edge cases: first and last ones are only connected to one of their kind and two of the other kind
    lenCTS = len(liste_CTS)
    lenCA = len(liste_CA)
    liste_CTS[0].ajouterVoisins([ (liste_CTS[1], cts_wire)
                                , (liste_CA[0], cts_ca_wire)
                                , (liste_CA[1], cts_ca_wire)])
    liste_CTS[-1].ajouterVoisins([(liste_CTS[-2], cts_wire)
                                 , (liste_CA[-1], cts_ca_wire)
                                 , (liste_CA[-2], cts_ca_wire)])
    for i in range(1, lenCTS -1): # omit first and last
        liste_CTS[i].ajouterVoisins([ (liste_CTS[(i-1)%lenCTS], cts_wire) # connected to 2 CTS
                                    , (liste_CTS[(i+1)%lenCTS], cts_wire)
                                    , (liste_CA[i%lenCA], cts_ca_wire) # connected to 3 CA
                                    , (liste_CA[(i-1)%lenCA], cts_ca_wire)
                                    , (liste_CA[(i+1)%lenCA], cts_ca_wire)])

    # for CA
    liste_CA[0].ajouterVoisins([ (liste_CA[1], ca_wire)
                               , (liste_CTS[0], cts_ca_wire)
                               , (liste_CTS[1], cts_ca_wire)])
    liste_CA[-1].ajouterVoisins([ (liste_CA[-2], ca_wire)
                                , (liste_CTS[-1], cts_ca_wire)
                                , (liste_CTS[-2], cts_ca_wire)])
    for i in range(1, lenCA -1): # omit first and last
        liste_CA[i].ajouterVoisins([ (liste_CA[(i-1)%lenCA], ca_wire) # connected to 2 CA
                                   , (liste_CA[(i+1)%lenCA], ca_wire)
                                   , (liste_CTS[(i+1)%lenCTS], cts_ca_wire) # connected to 3 CTS
                                   , (liste_CTS[i%lenCTS], cts_ca_wire)
                                   , (liste_CTS[(i-1)%lenCTS], cts_ca_wire)])  

    resultats = dict()

    # create the users
    # It is a list of list of users. Each list of users is a group of users connected to the same CA
    liste_users : List[List[User]] = list()
    for c in liste_CA:
        liste_users.append(list())
        for i in range(0, users_per_CA):
            user_adress = tuple(list(c.adresse[0:-1]) + [i+1])
            print(f"user : {user_adress} - CA : {c.adresse}")
            liste_users[-1].append(User(c, user_adress))
    printv(liste_users, isVerbose)
    flatten = lambda l: [] if l == [] else l[0] if len(l)==1 else l[0]+flatten(l[1:])
    flattened_list_user : List[User] = flatten(liste_users)

    #plots = plt.subplots(1,2)[1]
    plt.figure()


    diffPannes = [0]*len(Strategie)
    nbRefusInitial = [0]*10
    commutateurs = liste_CA+liste_CTS
    # Provoquer des pannes sur les liens
    for nbPanne in [0,5]: # Juste 5 pannes
        pannesCrees = list()

        # Création des pannes
        for _ in range(nbPanne):
            comPanneExt1 = commutateurs[random.randint(0,len(commutateurs)-1)]
            while len(comPanneExt1.voisins) == 0:
                comPanneExt1 = commutateurs[random.randint(0,len(commutateurs)-1)]
            adsVoisins = list(comPanneExt1.voisins.keys())
            comPanneExt2 = comPanneExt1.voisins[adsVoisins[random.randint(0,len(adsVoisins)-1)]][2]
            capacite = comPanneExt1.supprimerVoisin(comPanneExt2)
            pannesCrees.append((comPanneExt1, comPanneExt2, capacite))


        # Faire varier la stratégie
        for strategy in list(Strategie):
            label = printStrategy(strategy) + "" if nbPanne == 0 else " avec " + str(nbPanne) + " pannes"
            printv(f"Strategie : {label}", isVerbose)

            for commutateur in liste_CTS:
                commutateur.setStrategy(strategy)
            for commutateur in liste_CA:
                commutateur.setStrategy(strategy)

            charge, tauxRefus, diff = getChargeRefus(flattened_list_user, nbRefusInitial)

            if nbPanne == 0:
                #plots[0].plot(charge, tauxRefus, label=label)
                plt.plot(charge, tauxRefus, label=label)
                nbRefusInitial = diff
            else:
                diffPannes[strategy.value] = mean(diff)/MOYENNE

        # Rétablissement des pannes
        for (comPanneExt1, comPanneExt2, capacite) in pannesCrees:
            comPanneExt1.ajouterVoisin(comPanneExt2, capacite)

    for strategy in list(Strategie):
        pass#plots[1].bar(list(map(lambda s: printStrategy(s), Strategie)), diffPannes)

    #plots[0].set(xlabel="Charge in %", ylabel = "Refused call rate in %")
    #plots[1].set(xlabel = "Strategy", ylabel="Nombre d'appels refusés en plus")
    #plots[0].set_title("Evolution of refused call rate")
    #plots[1].set_title("Nombre de refus supplémentaires moyens pour une charge <=60% avec 5 pannes")
    #plots[0].legend()
    #plots[1].legend()
    plt.xlabel("Load in %")
    plt.ylabel("Refused call rate in %")
    plt.title("Evolution of refused call rate")
    plt.legend()
    plt.show()


else:
    print("Please run this script directly, not as a module.")