import argparse
import random
from Commutateur import Commutateur
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog = 'RouteComparer',
                    description = 'Program evaluating and comparing the performance of different routing algorithms',
                    epilog = 'Project for ENSEEIHT, 2023')
    parser.add_argument('-s', '--strategie',
                        help="strategy used between Statique, PartageCharge and Adaptative",
                        choices=['Statique', 'PartageCharge', 'Adaptative'],
                        dest='strategy',
                        required=True)
    parser.add_argument('-n', '--number_of_clients', dest='nc', default='10')
    parser.add_argument('-v', '--verbose', dest='verbose', default='False')
    args = vars(parser.parse_args())
    s = args.get('strategy')
    isVerbose = bool(args.get('verbose'))
    client_count = args.get('nc')
    CTS_count = 3
    CA_count = 4
    # when parsing is ok, create the network, and a list of clients
    #           1.0.0                  2.0.0                  3.0.0
    #           CTS1-------------------CTS2-------------------CTS3
    #            /\                     /\                     /\
    #           /  \                    
    #          /    \
    #         /      \
    #        |        \
    #        |         \        FLEMME
    #        |          \
    #        |           \
    #        |            \
    #        |             \
    #        |              \
    #        |               \
    #      1.1.0              \1.2.0               2.1.0
    #       CA1-----------------CA2-----------------CA3-----------------CA4      
    #        |                   |                   |                    |
    #        |                   |                   |                    |
    #        |                   |                   |                    |
    #    c[0]-c[n/4-1]     c[n/4]-c[n/2-1]      c[n/2]-c[3n/4-1]     c[3n/4]-c[n]
    adresses_CTS = random.sample(range(1, 10*CTS_count), CTS_count)
    adresses_CA = random.sample(range(1, 10*CA_count), CA_count)
    liste_CA: list(Commutateur) = []
    liste_CTS: list(Commutateur) = []
    for i in adresses_CTS:
        liste_CTS.append(Commutateur(str(i) + ".0.0"))
        
    for i in range(len(adresses_CA)):
        # choice: le address prefix of a CA is the same as the CTS of same idx. Ex: CA1 and CTS1 have same prefix
        liste_CA.append (Commutateur(str(adresses_CTS[i%len(adresses_CTS)]) + "." + str(adresses_CA[i]) + ".0"))
        
    print(liste_CTS)
    print(liste_CA)
    # Interconnection of the CTS
    # Edge cases: first and last ones are only connected to one neighbor
    liste_CTS[0].
    