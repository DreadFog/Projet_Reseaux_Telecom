from typing import List, Tuple

N = 3 # Taille des @ (N = 3 : A.B.C)

"""
@ : A.B.C
@com : A.B.0
A, B en communs -> dans la zone "3" (ie proche)
"""

class Commutateur:
    def __init__(self, adresse : List[int]):
        self.voisins = dict() # {@voisin -> [src1, src2], capacité du lien, voisin (objet)}
        self.adresse = adresse

    def ajouterVoisin(self, listeVoisins : List[Tuple[List[int], Tuple[List[List[int]], int, 'Commutateur']]]):
        #                   listVoisins :  [    (@voisin       ,      ([src1, src2], capacité, voisin (objet)))]
        for v in listeVoisins:
            self.voisins[str(v[0])] = v[1]

    def getVoisin(self, adrVoisin: List[int]) -> Tuple[List[List[int]], int, 'Commutateur']:
        return self.voisins[str(adrVoisin)]

    def demanderCommunicationStatique(self, adresseSource : List[int], adresseDestination : List[int]) -> bool:
        """Toujours le même choix de routage, calculé en fonction de l'adresse"""
        # Recherche du voisin : on compare les @ pour avoir celle la plus "proche" de l'@ dest
        resulats_i = []
        for vStr in [str(self.adresse)]+self.voisins:
            voisin = vStr.split('.')
            i = 0
            # Recherche de la zone qui diffère entre le commutateur actuel et l'@ dest
            while i < len(adresseDestination):
                if adresseDestination[i] != int(voisin[i]):
                    """Il faut changer de zone -> commuter"""
                    break
                i += 1
            resulats_i.append(i) # On ajoute la "distance" entre l'@ du voisin et l'@ dest
        i = resulats_i.index(max(resulats_i))
        adNextCommutateur = ([str(self.adresse)]+self.voisins)[i]


        if adNextCommutateur == self.adresse:
            # On est en liaison directe avec le destinataire
            comsEnCours.append(adresseSource)
            return True
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
            comsEnCours, capacitéLien, voisin = self.getVoisin(adNextCommutateur)
            assert not (adresseSource in comsEnCours)

            if len(comsEnCours) == capacitéLien:
                # Capacité maximale atteinte
                return False
            else:
                comsEnCours.append(adresseSource)
                return voisin.demanderCommunicationStatique(adresseSource, adresseDestination)

    def demanderCommunicationPartageCharge(self, adresseSource : List[int], adresseDestination : List[int]) -> bool:
        """Partage équitablement en fonction de la capacité totale des liens"""
        return True

    def demanderCommunicationAdaptative(self, adresseSource : List[int], adresseDestination : List[int]) -> bool:
        """Partage équitablement en fonction de la capacité restante des liens"""
        return True

    def fermerCommunication(self, adresseSource : List[int]):
        comsEnCours = self.getVoisin(adresseSource)[0]
        comsEnCours.remove(adresseSource)

    def __repr__(self) -> str:
        return str(self.adresse)