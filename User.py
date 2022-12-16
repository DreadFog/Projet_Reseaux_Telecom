from CA import *

class User:
    def __init__(self, commutateur : CA, adresse : str):
        self.adresse = adresse
        self.commutateur = commutateur

    def appel(self, adresseDestination : str):
        self.destinataire = adresseDestination
        self.commutateur.demanderCommunication(self.adresse, self.destinataire)
        pass
    
    def raccrocher(self):
        pass
