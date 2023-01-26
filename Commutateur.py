from typing import List, Tuple, Dict
from random import random
from enum import Enum
import numpy as np
from Dijkstra import Dijkstra

class Strategie(Enum):
    Statique = 0
    PartageCharge = 1
    Adaptative = 2
    Dijkstra = 3

def printStrategy(strategy) -> str :
    match strategy:
        case Strategie.Statique: return "Static"
        case Strategie.PartageCharge: return "LoadBalancing"
        case Strategie.Adaptative: return "Adaptative"
        case Strategie.Dijkstra: return "Dijkstra"
        case _: return "printStrategy non mis à jour"

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
CTS_count = 5
CA_count = CTS_count + 1
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
        """Ajout d'un lien unidirectionnel de self vers voisin"""
        adVoisin = voisin.adresse
        self.voisins[adVoisin] = ([], capacity, voisin)
        traffic_state[self.id][voisin.id] = capacity
    
    def supprimerVoisin(self, voisin : 'Commutateur'):
        """Suppression d'un et un seul lien unidirectionnel de self vers voisin
           Return: la capacité du lien en panne
        """
        adVoisin = voisin.adresse
        capacite = self.voisins[adVoisin][1]
        assert len(self.voisins.pop(adVoisin)[0]) == 0
        traffic_state[self.id][voisin.id] = 0
        return capacite

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

    def _getNeighbour(self, adressesAccessibles, adresseDestination):
        voisin_proche = list()
        resultats_i = list()
        adressesAccessibles = [self.adresse]+list(self.voisins.keys())
        for voisin in adressesAccessibles:
            # Sert si aucun voisin dans la zone de destination, pour se rapprocher de la zone
            voisin_proche.append(abs(voisin[0]-adresseDestination[0]))
            # On ajoute la "distance" entre l'@ du voisin et l'@ dest
            resultats_i.append(self._getZone(adresseDestination, voisin))
        return resultats_i, voisin_proche

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
        adressesAccessibles = [self.adresse]+list(self.voisins.keys())
        printv(f"Adresses acecessibles : {adressesAccessibles}", verbose)
        resultats_i, voisin_proche = self._getNeighbour(adressesAccessibles, adresseDestination)

        if resultats_i[0] == (N-1):
            i = 0
        elif max(resultats_i) == resultats_i[0]:
            i = voisin_proche.index(min(voisin_proche))
            # On a pas de voisin qui a une zone en commun avec l'@ dest, on s'en rapproche
        else:
            i = resultats_i.index(max(resultats_i))
        adNextCommutateur = adressesAccessibles[i]
        if adNextCommutateur == self.adresse and resultats_i[0] < N-1:
            printv(f"@ commutateur : {self.adresse} | @ destination : {adresseDestination}", verbose)
            # Cas où on "maximise" la distance mais on est pas en liaison directe
            # -> on ne peut pas trouver de route (avec notre topologie ! sinon avec 1 étage de plus tout change)
            # Ne peut arriver qu'en cas de panne
            return (False, [])

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
        adressesAccessibles : List[tuple] = [self.adresse]+list(self.voisins.keys())
        printv(f"Liste des adresses accessibles : {adressesAccessibles}", verbose)
        resultats_i, voisin_proche = self._getNeighbour(adressesAccessibles, adresseDestination)

        if resultats_i[0] == (N-1):
            adNextCommutateur = self.adresse
        else:
            # "Distance" entre le commutateur self et la destination
            d = resultats_i[0]
            if max(resultats_i) == d:
                j = voisin_proche.index(min(voisin_proche))
                indexes_possibles = [index for index in range(1,len(voisin_proche)) \
                                        if voisin_proche[index]==voisin_proche[j] and voisin_proche[index]!=voisin_proche[0]]
            else:
                # Indices des voisins nous rapprochant de la destination
                indexes_possibles = [index for index in range(len(resultats_i)) if resultats_i[index]>d]
            printv(f"Nombres de commutateurs qui nous rapprochent de la destination : {len(indexes_possibles)}", verbose)
            if len(indexes_possibles) == 0:
                return (False, [])
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
        adressesAccessibles = [self.adresse]+list(self.voisins.keys())
        resultats_i, voisin_proche = self._getNeighbour(adressesAccessibles, adresseDestination)

        if resultats_i[0] == (N-1):
            adNextCommutateur = self.adresse
        else:
            # "Distance" entre le commutateur self et la destination
            d = resultats_i[0]
            if max(resultats_i) == d:
                j = voisin_proche.index(min(voisin_proche))
                # On liste les voisins qui nous rapprochent
                indexes_possibles = [index for index in range(1,len(voisin_proche)) \
                                        if voisin_proche[index]==voisin_proche[j] and voisin_proche[index]!=voisin_proche[0]]
            else:
                # Indices des voisins nous rapprochant de la destination
                indexes_possibles = [index for index in range(len(resultats_i)) if resultats_i[index]>d]
            if len(indexes_possibles) == 0:
                return (False, [])
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
        #pred = dijkstra(csgraph=1/traffic_state, indices=self.id, return_predecessors=True)[1]
        pred = Dijkstra(G=1/traffic_state, s=self.id, lci=lambda x,y: x+y)[1]
        if pred[idDest] == -9999:
            # On ne peut pas faire d'appel vers l'@ dest
            return (False, list())

        chemin = [self.adresse]
        dictKeys = list(dictAdComId.keys())
        valuesOfDict = list(map(lambda x: x[1], dictAdComId.values()))
        while idDest != self.id:
            # modification de la matrice de traffic, celle-ci reste symétrique
            #traffic_state[idDest][pred[idDest]] -= 1
            traffic_state[pred[idDest]][idDest] -= 1
            # Indices dans la liste des clés du dictionnaire des commutateurs en fin de chemin
            indexIdDest = valuesOfDict.index(idDest)
            indexIdDestP = valuesOfDict.index(pred[idDest])
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
            printv(f"Liaison avec le prochain voisin : {voisinProchainSaut}", verbose)
            voisinProchainSaut[0].remove(adresseSource)
            voisinProchainSaut[2].fermerCommunication(adresseSource)
            # déblocage de la communication dans la matrice de traffic
            traffic_state[self.id][voisinProchainSaut[2].id] += 1
            #traffic_state[voisinProchainSaut[2].id][self.id] += 1
            self.prochainCom.pop(adresseSource)
        except KeyError:
            # par construction, une erreur signifie qu'on est au cas terminal de la fermeture de communication.
            pass

    def __repr__(self) -> str:
        return str(self.adresse)
