from Commutateur import Commutateur, Strategie

class User:
    def __init__(self, commutateur : Commutateur, adresse : tuple):
        self.adresse = adresse
        self.commutateur = commutateur

    def appel(self, adresseDestination : tuple, strategie : Strategie) -> bool:
        print(f"Stratégie adoptée : {strategie}")
        methodeAppel = { Strategie.Statique : self.commutateur.demanderCommunicationStatique \
                       , Strategie.PartageCharge : self.commutateur.demanderCommunicationPartageCharge \
                       , Strategie.Adaptative : self.commutateur.demanderCommunicationAdaptative}
        self.destinataire = adresseDestination
        appelOK = methodeAppel[strategie](self.adresse, self.destinataire)
        if not(appelOK):
            print(f"Appel refusé pour le client à l'adresse {self.adresse}")
        return appelOK

    def raccrocher(self):
        self.commutateur.fermerCommunication(self.adresse)
        
    def __repr__(self) -> str:
        return f"User({self.adresse})"
