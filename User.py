from Commutateur import Commutateur, Strategie, printv, printAdress


class User:
    def __init__(self, commutateur : Commutateur, adresse : tuple):
        self.adresse = adresse
        self.commutateur = commutateur

    def appel( self, adresseDestination : tuple\
             , verbose = False) -> bool:
        self.destinataire = adresseDestination
        appelOK, trace = self.commutateur.demanderCommunication(self.adresse, self.destinataire, verbose)
        if not(appelOK):
            printv(f"Appel refusé pour le client à l'adresse {self.adresse}", verbose)
        else:
            if verbose:
                print("====== TRACE ======")
                l = list(map(printAdress, [self.adresse]+trace))
                print(*l)
        return appelOK

    def raccrocher(self, verbose):
        self.commutateur.fermerCommunication(self.adresse, verbose)
        
    def __repr__(self) -> str:
        return f"User({self.adresse})"
