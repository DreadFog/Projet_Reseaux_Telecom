from Commutateur import Commutateur
from typing import List

class User:
    def __init__(self, commutateur : Commutateur, adresse : List[int]):
        self.adresse = adresse
        self.commutateur = commutateur

    def appel(self, adresseDestination : List[int]) -> bool:
        self.destinataire = adresseDestination
        appelOK = self.commutateur.demanderCommunicationStatique(self.adresse, self.destinataire)
        if not(appelOK):
            print(f"Appel refusé pour le client à l'adresse {self.adresse}")
        return appelOK

    def raccrocher(self):
        self.commutateur.fermerCommunication(self.adresse)
