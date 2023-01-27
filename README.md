# Exemple de lancement
## Charactéristiques de cette simulation :
    - 3 personnes
    - 2 CTSs
    - 3 CAs
    - Stratégie utilisée : Pratage de charge
    - Pourcentage de charge : 10%
    - Capacité des liens CTS-CTS : 5
    - Capacité des liens CTS-CA : 3
    - Capacité des liens CA-CA : 1

## Résultat du mode verbose :
```ps
>> python3 ./main.py -v v -n 3
Users per CA: 1
(1, 0, 0)
(2, 0, 0)
-------CTSs-------
CTS : (1, 0, 0)
(2, 0, 0) (1, 1, 0) (1, 2, 0) (2, 3, 0)
CTS : (2, 0, 0)
(1, 0, 0) (2, 3, 0) (1, 2, 0) (1, 1, 0)
-------CAs-------
CA : (1, 1, 0)
(1, 2, 0) (1, 0, 0) (2, 0, 0)
CA : (1, 2, 0)
(1, 1, 0) (2, 3, 0) (1, 0, 0) (2, 0, 0)
CA : (2, 3, 0)
(1, 2, 0) (1, 0, 0) (2, 0, 0)
user : (1, 1, 1) - CA : (1, 1, 0)
user : (1, 2, 1) - CA : (1, 2, 0)
user : (2, 3, 1) - CA : (2, 3, 0)
[[User((1, 1, 1))], [User((1, 2, 1))], [User((2, 3, 1))]]
[[0. 5. 2. 2. 2.]
 [5. 0. 2. 2. 2.]
 [2. 2. 0. 1. 0.]
 [2. 2. 1. 0. 1.]
 [2. 2. 0. 1. 0.]]
Strategie : LoadBalancing
Nombre de pannes : 0
Charge du réseau : 10%
0 / 1, users : 3, users_count : 3
Appel de (1, 2, 1) vers (2, 3, 1)
Demande de communication sur le commutateur :                 (1, 2, 0) de (1, 2, 1) vers (2, 3, 1)
Liste des adresses accessibles : [(1, 2, 0), (1, 1, 0), (2, 3, 0), (1, 0, 0), (2, 0, 0)]
Nombres de commutateurs qui nous rapprochent de la destination : 1
Liste des capacités associées aux voisins : [1]
====== TRACE ======
1.2.1 1.2.0 1.1.0 1.1.1
1.2.1 raccroche sur 1.2.0...
Liaison avec le prochain voisin : ([(1, 2, 1)], 1, (1, 1, 0))
Appel de (1, 2, 1) vers (2, 3, 1)
Demande de communication sur le commutateur :                 (1, 2, 0) de (1, 2, 1) vers (2, 3, 1)
Liste des adresses accessibles : [(1, 2, 0), (1, 1, 0), (2, 3, 0), (1, 0, 0), (2, 0, 0)]
Nombres de commutateurs qui nous rapprochent de la destination : 2
Liste des capacités associées aux voisins : [1, 2]
====== TRACE ======
1.2.1 1.2.0 2.0.0 2.3.0 2.3.1
1.2.1 raccroche sur 1.2.0...
Liaison avec le prochain voisin : ([(1, 2, 1)], 2, (2, 0, 0))
No artists with labels found to put in legend.  Note that artists whose label start with an underscore are ignored when legend() is called with no argument.
```