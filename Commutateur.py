from typing import List, Tuple, Dict
from random import random
from enum import Enum

class Strategie(Enum):
    Statique = 0
    PartageCharge = 1
    Adaptative = 2

N = 3 # Taille des @ (N = 3 : A.B.C)
"""
N : taille des adresses (de la forme @ : A.B.C)
@com : A.B.0
A, B en communs -> dans la zone "3" (ie proche)
"""
listInt2Str = lambda l: "" if l == [] else str(l[0]) if len(l) == 1 else str(l[0])+"."+listInt2Str(l[1:])

class Commutateur:

    def __init__(self, adresse : list):
        # {@voisin -> [src1, src2], capacité du lien, voisin (objet)}
        self.voisins : Dict[tuple, Tuple[List[tuple], int, Commutateur]] = dict() 

        # Conversion en tuple pour pouvoir être utilisé comme clé dans un dictionnaire
        self.adresse = tuple(adresse) 

        # Associe une communication en cours au prochain saut
        # Un élément par communication en cours
        self.prochainCom = dict() # {@Source -> prochain commutateur}

    def ajouterVoisin(self, listeVoisins : List[Tuple[tuple, Tuple[List[tuple], int, 'Commutateur']]]):
        #                   listVoisins :  [    (@voisin       ,      ([src1, src2], capacité, voisin (objet)))]
        for v in listeVoisins:
            ad : tuple = v[0]
            self.voisins[ad] = v[1]

    def getVoisin(self, adrVoisin: tuple) -> Tuple[List[tuple], int, 'Commutateur']:
        return self.voisins[adrVoisin]

    def demanderCommunicationStatique( self, adresseSource  : tuple \
                                     , adresseDestination   : tuple, verbose = False) \
                                                            -> Tuple[bool,List[tuple]]:
        """Toujours le même choix de routage, calculé en fonction de l'adresse"""
        if verbose:
            print(f"Demande de communication sur le commutateur : {self.adresse} de {adresseSource} vers {adresseDestination}")
        # Recherche du voisin : on compare les @ pour avoir celle la plus "proche" de l'@ dest
        resulats_i = list()
        voisin_proche = list()
        adressesAccessibles = [self.adresse]+list(self.voisins.keys())
        if verbose:
            print(f"Adresses acecessibles : {adressesAccessibles}")
        for voisin in adressesAccessibles:
            #print(f"Voisin : {voisin} de type : {type(voisin)}")
            
            # Sert si aucun voisin dans la zone de destination, pour se rapprocher de la zone
            voisin_proche.append(abs(voisin[0]-adresseDestination[0]))
            i = 0
            
            # Recherche de la zone qui diffère entre le commutateur actuel et l'@ dest
            while i < len(adresseDestination):
                if adresseDestination[i] != voisin[i]:
                    """Il faut changer de zone -> commuter"""
                    break
                i += 1
            resulats_i.append(i) # On ajoute la "distance" entre l'@ du voisin et l'@ dest
        i = resulats_i.index(max(resulats_i))
        j = voisin_proche.index(min(voisin_proche))
        if max(resulats_i) == 0:
            # On a pas de voisin qui a une zone en commun avec l'@ dest, on s'en rapproche
            adNextCommutateur = adressesAccessibles[j]
        else:
            adNextCommutateur = adressesAccessibles[i]
        if verbose:
            print(f"Prochain Saut de {self.adresse} vers {adNextCommutateur}")
            print(f"voisin choisi : {self.voisins}")


        if adNextCommutateur == self.adresse:
            # On est en liaison directe avec le destinataire
            return (True, [self.adresse, adresseDestination])
        else:
            # Recherche du voisin:
            # self ∩ @dest : adresseDestination[0:i-1].0.0.0 
            # -> il faut contacter adresseDestination[0:i-k].0.0.0
            # qui soit dans nos voisins avec k le + petit.
            # Dans la structure, chacun a pour voisin tous les commutateurs de la zone supérieure.
            #k = 1
            #adNextCommutateur = adresseDestination[0:i-k] + [0]*(N-k)
            #while k < N and not(adNextCommutateur in self.voisins):
            #    k+=1
            #    adNextCommutateur = adresseDestination[0:i-k] + [0]*(N-k)

            #assert not (k == N and not(adNextCommutateur in self.voisins))

            # On a le prochain saut : il faut vérifier que la capacité du lien
            # est OK et enregistrer l'@ source dans les communications en cours
            comsEnCours, capacitéLien, voisin = self.voisins[adNextCommutateur]
            assert not (adresseSource in comsEnCours)

            if len(comsEnCours) == capacitéLien:
                # Capacité maximale atteinte
                return (False, [])
            else:
                comEtablie, trace = voisin.demanderCommunicationStatique(adresseSource, adresseDestination)
                if comEtablie:
                    self.prochainCom[adresseSource] = adNextCommutateur
                    comsEnCours.append(adresseSource)
                return (comEtablie, [self.adresse] + trace)

    def demanderCommunicationPartageCharge( self, adresseSource : tuple\
                                          , adresseDestination : tuple, verbose = False) \
                                                            -> Tuple[bool,List[tuple]]:
        """Partage équitablement en fonction de la capacité totale des liens"""
        if verbose:
            print(f"Demande de communication sur le commutateur : {self.adresse} de {adresseSource} vers {adresseDestination}")
        # Soit on est en liaison directe, soit on envoi à la couche supérieure ou la même couche de manière random
        # Recherche des voisin possibles : on compare les @ pour se "raprocher" de l'@ dest
        resulats_i = list()
        adressesAccessibles : List[tuple] = [self.adresse]+list(self.voisins.keys())
        if verbose:
            print(f"Liste des adresses accessibles : {adressesAccessibles}")
        for voisin in adressesAccessibles:
            i = 0
            # Recherche de la zone qui diffère entre le commutateur actuel et l'@ dest
            while i < len(adresseDestination):
                if adresseDestination[i] != voisin[i]:
                    """Il faut changer de zone -> commuter"""
                    break
                i += 1
            resulats_i.append(i) # On ajoute la "distance" entre l'@ du voisin et l'@ dest
        if resulats_i[0] == (N-1):
            adNextCommutateur = self.adresse
        else:
            # "Distance" entre le commutateur self et la destination
            d = resulats_i[0]
            # Indices des voisins nous rapprochant de la destination
            indexes_possibles = [index for index in range(len(resulats_i)) if resulats_i[index]>d]
            # Adresses des voisins nous rapprochant de la destination
            ad_voisins_possibles = [adressesAccessibles[i] for i in indexes_possibles]
            capacites_voisins = [self.getVoisin(adNextComPossible)[1] for adNextComPossible in ad_voisins_possibles]
            if verbose:
                print(f"Liste des capacités associées aux voisins : {capacites_voisins}")
            # Choix de l'indice avec pondération en fonction de la capacité des liens
            rand_capacites = [c*random() for c in capacites_voisins]
            ind_voisin = rand_capacites.index(max(rand_capacites))
            adNextCommutateur = ad_voisins_possibles[ind_voisin]
        
        if adNextCommutateur == self.adresse:
            # On est en liaison directe avec le destinataire
            return (True, [self.adresse, adresseDestination])
        else:
            # On a le prochain saut : il faut vérifier que la capacité du lien
            # est OK et enregistrer l'@ source dans les communications en cours
            comsEnCours, capacitéLien, voisin = self.getVoisin(adNextCommutateur)
            assert not (adresseSource in comsEnCours)
            if len(comsEnCours) == capacitéLien:
                # Capacité maximale atteinte
                return (False, [])
            else:
                comEtablie, trace = voisin.demanderCommunicationPartageCharge(adresseSource, adresseDestination)
                if comEtablie:
                    self.prochainCom[adresseSource] = adNextCommutateur
                    comsEnCours.append(adresseSource)
                return (comEtablie, [self.adresse] + trace)

    def demanderCommunicationAdaptative( self, adresseSource : tuple\
                                       , adresseDestination : tuple, verbose = False) \
                                                            -> Tuple[bool,List[tuple]]:
        """Partage équitablement en fonction de la capacité restante des liens"""
        # Soit on est en liaison directe, soit on envoi à la couche supérieure ou la même couche de manière random
        # Recherche des voisin possibles : on compare les @ pour se "raprocher" de l'@ dest
        resulats_i = list()
        adressesAccessibles = [self.adresse]+list(self.voisins.keys())
        for voisin in adressesAccessibles:
            i = 0
            # Recherche de la zone qui diffère entre le commutateur actuel et l'@ dest
            while i < len(adresseDestination):
                if adresseDestination[i] != voisin[i]:
                    """Il faut changer de zone -> commuter"""
                    break
                i += 1
            resulats_i.append(i) # On ajoute la "distance" entre l'@ du voisin et l'@ dest
        
        if resulats_i[0] == (N-1):
            adNextCommutateur = self.adresse
        else:
            # "Distance" entre le commutateur self et la destination
            d = resulats_i[0]
            # Indices des voisins nous rapprochant de la destination
            indexes_possibles = [index for index in range(len(resulats_i)) if resulats_i[index]>d]
            # Adresses des voisins nous rapprochant de la destination
            ad_voisins_possibles = [adressesAccessibles[i] for i in indexes_possibles]
            capacites_voisins = [self.getVoisin(adNextComPossible)[1] for adNextComPossible in ad_voisins_possibles]
            # Choix de l'indice avec pondération en fonction de la capacité des liens **restante**
            rand_capacites = [random()*(capacites_voisins[c]-len(self.getVoisin(ad_voisins_possibles[c])[0])) \
                                        for c in range(len(capacites_voisins))]
            ind_voisin = rand_capacites.index(max(rand_capacites))
            adNextCommutateur = ad_voisins_possibles[ind_voisin]
        
        if adNextCommutateur == self.adresse:
            # On est en liaison directe avec le destinataire
            return (True, [self.adresse, adresseDestination])
        else:
            # On a le prochain saut : il faut vérifier que la capacité du lien
            # est OK et enregistrer l'@ source dans les communications en cours
            comsEnCours, capacitéLien, voisin = self.getVoisin(adNextCommutateur)
            assert not (adresseSource in comsEnCours)
            if len(comsEnCours) == capacitéLien:
                # Capacité maximale atteinte
                return (False, [])
            else:
                comEtablie, trace = voisin.demanderCommunicationPartageCharge(adresseSource, adresseDestination)
                if comEtablie:
                    self.prochainCom[adresseSource] = adNextCommutateur
                    comsEnCours.append(adresseSource)
                return (comEtablie, [self.adresse] + trace)

    def fermerCommunication(self, adresseSource : tuple):
        adresseVoisinProchainSaut = self.prochainCom[adresseSource]
        voisinProchainSaut = self.getVoisin(adresseVoisinProchainSaut)
        voisinProchainSaut[0].remove(adresseSource)
        voisinProchainSaut[2].fermerCommunication(adresseSource)
        self.prochainCom.pop(adresseSource)

    def __repr__(self) -> str:
        return str(self.adresse)
