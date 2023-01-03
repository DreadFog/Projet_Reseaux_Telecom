from Commutateur import Commutateur, Strategie

def printAdress(ad : tuple) -> str:
    match len(ad):
        case 0: return "\n"
        case 1: return str(ad[0])
        case _: return str(ad[0])+"."+printAdress(ad[1:])

class User:
    def __init__(self, commutateur : Commutateur, adresse : tuple):
        self.adresse = adresse
        self.commutateur = commutateur

    def appel( self, adresseDestination : tuple\
             , strategie : Strategie, verbose = False) -> bool:
        if verbose:
            print(f"Stratégie adoptée : {strategie}")
        methodeAppel = { Strategie.Statique : self.commutateur.demanderCommunicationStatique \
                       , Strategie.PartageCharge : self.commutateur.demanderCommunicationPartageCharge \
                       , Strategie.Adaptative : self.commutateur.demanderCommunicationAdaptative}
        self.destinataire = adresseDestination
        appelOK, trace = methodeAppel[strategie](self.adresse, self.destinataire, verbose)
        if not(appelOK):
            print(f"Appel refusé pour le client à l'adresse {self.adresse}")
        else:
            print("====== TRACE ======")
            l = list(map(printAdress, [self.adresse]+trace))
            print(*l)
        return appelOK

    def raccrocher(self):
        self.commutateur.fermerCommunication(self.adresse)
        
    def __repr__(self) -> str:
        return f"User({self.adresse})"
