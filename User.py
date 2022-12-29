from Commutateur import *

class User:
    def __init__(self, commutateur : Commutateur, adresse : List[int]):
        self.adresse = adresse
        self.commutateur = commutateur

    def appel(self, adresseDestination : List[int]) -> bool:
        self.destinataire = adresseDestination
        return self.commutateur.demanderCommunication(self.adresse, self.destinataire)

    def raccrocher(self):
        self.commutateur.fermerCommunication(self.adresse)
