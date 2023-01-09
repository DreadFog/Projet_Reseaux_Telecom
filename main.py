import argparse
import random
from Commutateur import Commutateur, Strategie, printv
from User import User
from typing import List

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'RouteComparer',
                    description = 'Program evaluating and comparing the performance of different routing algorithms',
                    epilog = 'Project for ENSEEIHT, 2023')
    parser.add_argument('-s', '--strategie',
                        help="strategy used between Statique, PartageCharge and Adaptative",
                        choices=['Statique', 'PartageCharge', 'Adaptative'],
                        dest='strategy',
                        default="Statique")
    parser.add_argument('-n', '--number_of_users', dest='nc', default=10)
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
        case _:
            print("Error: unknown strategy. Defaulting to Statique")
            chosenStrategy = Strategie.Statique
    print("Strategy chosen : " + str(chosenStrategy).split('.')[1])

    isVerbose = bool(args.get('verbose'))
    users_count : int|None = args.get('nc')
    CTS_count = 3
    CA_count = 4
    users_per_CA = users_count // CA_count if users_count != None else -1
    print("Users per CA: {}".format(users_per_CA))
    nb_appels_refuse = 0
    # capacity of the links
    cts_wire = 10
    ca_wire = 2
    cts_ca_wire = 5
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
    adresses_CTS = range(1, CTS_count)
    adresses_CA = range(1, CA_count)
    liste_CA: list[Commutateur] = list()
    liste_CTS: list[Commutateur] = list()
    for i in adresses_CTS:
        liste_CTS.append(Commutateur((i,0,0), chosenStrategy))

    for i in range(len(adresses_CA)):
        # choice: address prefix of a CA is the same as the CTS of same idx. Ex: CA1 and CTS1 have same prefix
        liste_CA.append(Commutateur((adresses_CTS[i%len(adresses_CTS)],adresses_CA[i],0), chosenStrategy))

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
    # create the users
    # It is a list of list of users. Each list of users is a group of users connected to the same CA
    liste_users : List[List[User]] = list()
    for c in liste_CA:
        liste_users.append(list())
        for i in range(0, users_per_CA):
            user_adress = tuple(list(c.adresse[0:-1]) + [i+1])
            liste_users[-1].append(User(c, user_adress))
    printv(liste_users, isVerbose)

    flatten = lambda l: [] if l == [] else l[0] if len(l)==1 else l[0]+flatten(l[1:])
    flattened_list_user : List[User] = flatten(liste_users)

    # Calls
    for client in flattened_list_user:
        client_dest = flattened_list_user[random.randint(0, len(flattened_list_user)-1)]
        # Eviter qu'un client s'appelle lui-même
        while (client_dest == client):
            client_dest = flattened_list_user[random.randint(0, len(flattened_list_user)-1)]
        printv(f"Appel de {client.adresse} vers {client_dest.adresse}", isVerbose)
        if not(client.appel(client_dest.adresse, isVerbose)):
            nb_appels_refuse += 1
    print(f"Nombre total d'appels refusés : {nb_appels_refuse} sur {len(flattened_list_user)} appels")
else:
    print("Please run this script directly, not as a module.")