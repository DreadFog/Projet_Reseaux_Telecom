from typing import List, Tuple, Dict
from random import random
from enum import Enum
import numpy as np
from scipy.sparse.csgraph import dijkstra

class Strategie(Enum):
    Statique = 0
    PartageCharge = 1
    Adaptative = 2
    Dijkstra = 3

def printv(s, verbose = False):
  if verbose:
    print(s)

def printAdress(ad : tuple) -> str:
    match len(ad):
        case 0: return "\n"
        case 1: return str(ad[0])
        case _: return str(ad[0])+"."+printAdress(ad[1:])

N = 3 # Taille des @ (N = 3 : A.B.C)
"""
N : taille des adresses (de la forme @ : A.B.C)
@com : A.B.0
A, B en communs -> dans la zone "3" (ie proche)
"""
CTS_count = 3
CA_count = 4
nbCommutateurs = CTS_count+CA_count
# Initialise la matrice des communications
traffic_state = np.zeros((nbCommutateurs, nbCommutateurs))

class Identifiant:
    def __init__(self):
        self.id = 0
    def giveID(self):
        self.id += 1
        return self.id-1

id = Identifiant()
dictAdComId : Dict[Tuple[int], Tuple['Commutateur', int]] = dict()

class Commutateur:
    def __init__(self, adresse : tuple, strategy: Strategie):
        # {@voisin -> [src1, src2], capacité du lien, voisin (objet)}
        self.voisins : Dict[tuple, Tuple[List[tuple], int, Commutateur]] = dict() 

        # Conversion en tuple pour pouvoir être utilisé comme clé dans un dictionnaire
        self.adresse = adresse 

        # Associe une communication en cours au prochain saut
        # Un élément par communication en cours
        self.prochainCom = dict() # {@Source -> prochain commutateur}
        # la stratégie du commutateur
        self.strategie = strategy
        self.id = id.giveID()
        dictAdComId[adresse] = (self, self.id)
    
    def setStrategy(self, strategie : Strategie):
        """Permet de changer la stratégie d'un commutateur: utile pour comparer les stratégies lors de tests"""
        self.strategie = strategie
    
    def demanderCommunication( self, adresseSource : tuple
                             , adresseDestination : tuple, verbose = False):
        methodeAppel = { Strategie.Statique        : self.demanderCommunicationStatique \
                       , Strategie.PartageCharge   : self.demanderCommunicationPartageCharge \
                       , Strategie.Adaptative      : self.demanderCommunicationAdaptative \
                       , Strategie.Dijkstra        : self.demanderCommunicationDijkstra} 
        return methodeAppel[self.strategie](adresseSource, adresseDestination, verbose)

    def ajouterVoisin(self, voisin : 'Commutateur', capacity : int):
        adVoisin = voisin.adresse
        self.voisins[adVoisin] = ([], capacity, voisin)
        traffic_state[self.id][voisin.id] = capacity
        
    def ajouterVoisins(self, listeVoisinsxCapacite : List[Tuple['Commutateur', int]]):
        #                    listeVoisinsxCapacite :  [(voisin (objet), capacité)]
        for voisin in listeVoisinsxCapacite:
            self.ajouterVoisin(voisin[0], voisin[1])

    def _getVoisin(self, adrVoisin: tuple) -> Tuple[List[tuple], int, 'Commutateur']:
        return self.voisins[adrVoisin]
    
    def _getZone(self, adresseDestination : tuple, voisin : tuple) -> int:
        """Recherche de la zone qui diffère entre le commutateur actuel et l'@ dest"""
        i = 0
        while i < len(adresseDestination):
            if adresseDestination[i] != voisin[i]:
                """Il faut changer de zone -> commuter"""
                break
            i += 1
        return i
    
    def _giveNextHop( self, adNextCommutateur : tuple
                    , adresseSource : tuple , adresseDestination : tuple):
        """Renvoi le résultat de l'appel : (appelOK, trace des commutateurs)"""
        if adNextCommutateur == self.adresse:
            # On est en liaison directe avec le destinataire
            return (True, [self.adresse, adresseDestination])
        else:
            # On a le prochain saut : il faut vérifier que la capacité du lien
            # est OK et enregistrer l'@ source dans les communications en cours
            comsEnCours, capacitéLien, voisin = self.voisins[adNextCommutateur]
            try:
                assert not (adresseSource in comsEnCours)
            except AssertionError:
                print(f"source {adresseSource}")
                raise AssertionError
            if len(comsEnCours) == capacitéLien:
                # Capacité maximale atteinte
                return (False, list())
            else:
                comEtablie, trace = voisin.demanderCommunication(adresseSource, adresseDestination)
                if comEtablie:
                    self.prochainCom[adresseSource] = adNextCommutateur
                    comsEnCours.append(adresseSource)
                return (comEtablie, [self.adresse] + trace)


    def demanderCommunicationStatique( self, adresseSource  : tuple \
                                     , adresseDestination   : tuple, verbose = False) \
                                                            -> Tuple[bool,List[tuple]]:
        """Toujours le même choix de routage, calculé en fonction de l'adresse"""
        printv(f"Demande de communication sur le commutateur :\
                 {self.adresse} de {adresseSource} vers {adresseDestination}", verbose)
        # Recherche du voisin : on compare les @ pour avoir celle la plus "proche" de l'@ dest
        resulats_i = list()
        voisin_proche = list()
        adressesAccessibles = [self.adresse]+list(self.voisins.keys())
        printv(f"Adresses acecessibles : {adressesAccessibles}", verbose)
        for voisin in adressesAccessibles:            
            # Sert si aucun voisin dans la zone de destination, pour se rapprocher de la zone
            voisin_proche.append(abs(voisin[0]-adresseDestination[0]))
            # On ajoute la "distance" entre l'@ du voisin et l'@ dest
            resulats_i.append(self._getZone(adresseDestination, voisin))

        if max(resulats_i) == 0:
            j = voisin_proche.index(min(voisin_proche))
            # On a pas de voisin qui a une zone en commun avec l'@ dest, on s'en rapproche
            adNextCommutateur = adressesAccessibles[j]
        else:
            i = resulats_i.index(max(resulats_i))
            adNextCommutateur = adressesAccessibles[i]

        printv(f"Prochain Saut de {self.adresse} vers {adNextCommutateur}\n \
                 voisin choisi : {self.voisins} ", verbose)

        return self._giveNextHop(adNextCommutateur, adresseSource, adresseDestination)

    def demanderCommunicationPartageCharge( self, adresseSource : tuple\
                                          , adresseDestination : tuple, verbose = False) \
                                                            -> Tuple[bool,List[tuple]]:
        """Partage équitablement en fonction de la capacité totale des liens"""
        printv(f"Demande de communication sur le commutateur :\
                 {self.adresse} de {adresseSource} vers {adresseDestination}", verbose)
        # Soit on est en liaison directe, soit on envoi à la couche supérieure ou la même couche de manière random
        # Recherche des voisin possibles : on compare les @ pour se "raprocher" de l'@ dest
        resulats_i = list()
        adressesAccessibles : List[tuple] = [self.adresse]+list(self.voisins.keys())
        printv(f"Liste des adresses accessibles : {adressesAccessibles}", verbose)
        for voisin in adressesAccessibles:
            # On ajoute la "distance" entre l'@ du voisin et l'@ dest
            resulats_i.append(self._getZone(adresseDestination, voisin))    

        if resulats_i[0] == (N-1):
            adNextCommutateur = self.adresse
        else:
            # "Distance" entre le commutateur self et la destination
            d = resulats_i[0]
            # Indices des voisins nous rapprochant de la destination
            indexes_possibles = [index for index in range(len(resulats_i)) if resulats_i[index]>d]
            # Adresses des voisins nous rapprochant de la destination
            ad_voisins_possibles = [adressesAccessibles[i] for i in indexes_possibles]
            capacites_voisins = [self._getVoisin(adNextComPossible)[1] for adNextComPossible in ad_voisins_possibles]
            printv(f"Liste des capacités associées aux voisins : {capacites_voisins}", verbose)
            # Choix de l'indice avec pondération en fonction de la capacité des liens
            rand_capacites = [c*random() for c in capacites_voisins]
            ind_voisin = rand_capacites.index(max(rand_capacites))
            adNextCommutateur = ad_voisins_possibles[ind_voisin]

        return self._giveNextHop(adNextCommutateur, adresseSource, adresseDestination)

    def demanderCommunicationAdaptative( self, adresseSource : tuple\
                                       , adresseDestination : tuple, verbose = False) \
                                                            -> Tuple[bool,List[tuple]]:
        """Partage équitablement en fonction de la capacité restante des liens"""
        # Soit on est en liaison directe, soit on envoi à la couche supérieure ou la même couche de manière random
        # Recherche des voisin possibles : on compare les @ pour se "raprocher" de l'@ dest
        resulats_i = list()
        adressesAccessibles = [self.adresse]+list(self.voisins.keys())
        for voisin in adressesAccessibles:
            # On ajoute la "distance" entre l'@ du voisin et l'@ dest
            resulats_i.append(self._getZone(adresseDestination, voisin))

        if resulats_i[0] == (N-1):
            adNextCommutateur = self.adresse
        else:
            # "Distance" entre le commutateur self et la destination
            d = resulats_i[0]
            # Indices des voisins nous rapprochant de la destination
            indexes_possibles = [index for index in range(len(resulats_i)) if resulats_i[index]>d]
            # Adresses des voisins nous rapprochant de la destination
            ad_voisins_possibles = [adressesAccessibles[i] for i in indexes_possibles]
            capacites_voisins = [self._getVoisin(adNextComPossible)[1] for adNextComPossible in ad_voisins_possibles]
            # Choix de l'indice avec pondération en fonction de la capacité des liens **restante**
            rand_capacites = [random()*(capacites_voisins[c]-len(self._getVoisin(ad_voisins_possibles[c])[0])) \
                                        for c in range(len(capacites_voisins))]
            ind_voisin = rand_capacites.index(max(rand_capacites))
            adNextCommutateur = ad_voisins_possibles[ind_voisin]

        return self._giveNextHop(adNextCommutateur, adresseSource, adresseDestination)

    def demanderCommunicationDijkstra( self, adresseSource : tuple\
                                     , adresseDestination : tuple, verbose = False) \
                                                            -> Tuple[bool,List[tuple]]:
        """Partage équitablement en fonction de la capacité restante des liens de tout le système"""
        # Parcours du chemin :
        # récupération de l'id destination
        # On remplace le dernier nombre de d'adresse du destinataire par 0
        adCommutateurFinal = tuple(list(adresseDestination[:-1])+[0]) # NIK
        idDest : int = dictAdComId[adCommutateurFinal][1]
        pred = dijkstra(csgraph=1/traffic_state, directed=False, indices=self.id, return_predecessors=True)[1]
        if pred[idDest] == -9999:
            # On ne peut pas faire d'appel vers l'@ dest
            return (False, list())

        chemin = [self.adresse]
        dictKeys = list(dictAdComId.keys())
        while idDest != self.id:
            # modification de la matrice de traffic, celle-ci reste symétrique
            traffic_state[idDest][pred[idDest]] -= 1
            traffic_state[pred[idDest]][idDest] -= 1
            # Indices dans la liste des clés du dictionnaire des commutateurs en fin de chemin
            indexIdDest = list(map(lambda x: x[1], dictAdComId.values())).index(idDest)
            indexIdDestP = list(map(lambda x: x[1], dictAdComId.values())).index(pred[idDest])
            # Adresses de ces dits commutateurs
            adNext = list(dictAdComId.keys())[indexIdDest]
            adNextP = list(dictAdComId.keys())[indexIdDestP]
            #com (pred[idDest]).prochainCom[adresseSource] = com(idDest)
            dictAdComId[adNextP][0].prochainCom[adresseSource] = dictAdComId[adNext][0]
            chemin.append(dictKeys[indexIdDest])
            idDest = pred[idDest]
            
        return (True, chemin+[adresseDestination])


    def fermerCommunication(self, adresseSource : tuple, verbose=False):
        printv(f"{printAdress(adresseSource)} raccroche sur {printAdress(self.adresse)}...", verbose)
        try:
            adresseVoisinProchainSaut = self.prochainCom[adresseSource]
            voisinProchainSaut = self._getVoisin(adresseVoisinProchainSaut)
            voisinProchainSaut[0].remove(adresseSource)
            voisinProchainSaut[2].fermerCommunication(adresseSource)
            # déblocage de la communication dans la matrice de traffic
            traffic_state[self.id][voisinProchainSaut[2].id] += 1
            traffic_state[voisinProchainSaut[2].id][self.id] += 1
            self.prochainCom.pop(adresseSource)
        except KeyError:
            # par construction, une erreur signifie qu'on est au cas terminal de la fermeture de communication.
            pass

    def __repr__(self) -> str:
        return str(self.adresse)
