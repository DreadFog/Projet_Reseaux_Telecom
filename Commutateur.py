from typing import List, Tuple, Dict
from random import random
from enum import Enum

class Strategie(Enum):
    Statique = 0
    PartageCharge = 1
    Adaptative = 2

def printv(s, verbose = False):
  if verbose:
    print(s)

N = 3 # Taille des @ (N = 3 : A.B.C)
"""
N : taille des adresses (de la forme @ : A.B.C)
@com : A.B.0
A, B en communs -> dans la zone "3" (ie proche)
"""

class Commutateur:

    def __init__(self, adresse : tuple):
        # {@voisin -> [src1, src2], capacité du lien, voisin (objet)}
        self.voisins : Dict[tuple, Tuple[List[tuple], int, Commutateur]] = dict() 

        # Conversion en tuple pour pouvoir être utilisé comme clé dans un dictionnaire
        self.adresse = adresse 

        # Associe une communication en cours au prochain saut
        # Un élément par communication en cours
        self.prochainCom = dict() # {@Source -> prochain commutateur}
    
    @staticmethod
    def demanderCommunication( routeur : 'Commutateur', strategie : Strategie, adresseSource : tuple
                             , adresseDestination : tuple, verbose = False):
        methodeAppel = { Strategie.Statique        : routeur.demanderCommunicationStatique \
                       , Strategie.PartageCharge   : routeur.demanderCommunicationPartageCharge \
                       , Strategie.Adaptative      : routeur.demanderCommunicationAdaptative}
        return methodeAppel[strategie](adresseSource, adresseDestination, verbose)

    def ajouterVoisin(self, voisin : 'Commutateur', capacity : int):
        adVoisin = voisin.adresse
        self.voisins[adVoisin] = ([], capacity, voisin)

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
    
    def _giveNextHop( self, adNextCommutateur : tuple,  strategie : Strategie
                    , adresseSource : tuple , adresseDestination : tuple):
        """Renvoi le résultat de l'appel : (appelOK, trace des commutateurs)"""
        if adNextCommutateur == self.adresse:
            # On est en liaison directe avec le destinataire
            return (True, [self.adresse, adresseDestination])
        else:
            # On a le prochain saut : il faut vérifier que la capacité du lien
            # est OK et enregistrer l'@ source dans les communications en cours
            comsEnCours, capacitéLien, voisin = self.voisins[adNextCommutateur]
            assert not (adresseSource in comsEnCours)

            if len(comsEnCours) == capacitéLien:
                # Capacité maximale atteinte
                return (False, [])
            else:
                comEtablie, trace = Commutateur.demanderCommunication(voisin, strategie, adresseSource, adresseDestination)
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

        return self._giveNextHop(adNextCommutateur, Strategie.Statique, adresseSource, adresseDestination)

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

        return self._giveNextHop(adNextCommutateur, Strategie.PartageCharge, adresseSource, adresseDestination)

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

        return self._giveNextHop(adNextCommutateur, Strategie.Adaptative, adresseSource, adresseDestination)

    def fermerCommunication(self, adresseSource : tuple):
        adresseVoisinProchainSaut = self.prochainCom[adresseSource]
        voisinProchainSaut = self._getVoisin(adresseVoisinProchainSaut)
        voisinProchainSaut[0].remove(adresseSource)
        voisinProchainSaut[2].fermerCommunication(adresseSource)
        self.prochainCom.pop(adresseSource)

    def __repr__(self) -> str:
        return str(self.adresse)
