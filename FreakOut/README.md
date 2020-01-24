# Lancement du jeu
Le jeu utilise le module python pygame. Pour l'installer, il faut faire la commande suivante
```bash
python3 -m pip install -U pygame --user
```
Lors que le jeu est télécharger, il se lance avec la commande, depuis le répertoire FreakOut
```bash
python3 Main.py arg1 arg2
```
arg1 correspond au temps max de non réactivité du joeur. Si l'arg1 n'est pas spécifié, le temps sera de 10 secondes
arg2 = "-d", lance le mode "developer" qui permet de jouer directement dans le terminale. Si l'arg2 n'est pas spécifié, le jeu utilisera une interface graphique

# Déroulement du jeu
Chaque joueur à des touches qui lui sont attribuées. Chaque touches correspond à une carte de la main du joueur (la touche est précisée sur la carte).
Lorsqu'un joueur appuis sur une touche qui est attribuée à une des ses cartes, celle-ci sera jouée.

Le joueur qui n'a plus de carte à gagné. Si la pile est vide et que un joueur doit piocher (=faute), le jeu se termine, aucun joueur n'a gagné.

# Quitter le jeu
On peut quitter le jeu en pleine partie ou a la fin de la partie en appuyant sur 'esc'
