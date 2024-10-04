README  

Ce code permet de simuler le déplacement d'un hexapode en utilisant des décharges neuronales.   

Fonctionnalités implémentées:   

L'avancement,   
Le recul,   
Le tournage à droite et à gauche,   
La modulation de la vitesse  
La simulation d'un déplacement approprié en fonction de son emplacement.   

  

Notre Modèle :  

Pour simuler la locomotion d'un hexapode, nous avons utilisé l'équation du modèle de neurone LIF (Leaky Integrate-and-Fire). 
Chaque patte de l'hexapode est contrôlée par deux neurones : un pour avancer et un pour reculer. 
Lorsqu'un spike est généré par le neurone "avancer", cela signifie que la patte avance. 
Lorsqu'un spike est généré par le neurone "reculer", cela signifie que la patte recule.  

  

Configuration  :

Il y a différents paramètres à définir pour définir quelle est l'action a réaliser et quel est le contexte d'environnement.

Les paramètres sont : 

TURN : Direction de rotation (0 = tout droit, 1 = gauche, 2 = droite), et l'action de tourner commence dès le debut.

ACTION : Action à effectuer (2 = avancer, 1 = reculer).  

NB_PATTES : Nombre de pattes de l'hexapode (doit être pair et supérieur à 6).  

VITESSE : Vitesse de déplacement (1 ou 2).  

TOURNER_EN_ROND : Indique si l'hexapode doit tourner en rond (1 = vrai, 0= faux).  

PRESCENCE_OBSTACLE : Indique la présence d'un obstacle (True ou False).  

position : Position de l'obstacle (1 = devant, 2= derrière 3 = droite, 4 = gauche).  

temps_apparition : Temps d'apparition de l'obstacle.  

temps_action : Temps pour gérer l'obstacle.  

  

Conditions d’utilisation :
1) Pour toutes les actions (Avancer, reculer, tourner, et pour l'ajout d'un obstacle), mettre VITESSE = 1
2) Pour une première simulation, il est conseillé de mettre PRESCENCE_OBSTACLE à False, TOURNER_EN_ROND à 0, et NB_PATTES à 6 et VITESSE =1.
3) On rencontre un obstacle que en avançant, c'est à dire qu'il faut mettre ACTION =2 si PRESCENCE_OBSTACLE = True.
4) On ne tourne en rond que en avançant
5) Il est préférable de mettre un temps d'apparition de l'obstacle et le temps d'action à un multiple de 6.
6) Pour tester VITESSE =2 , mettre PRESCENCE_OBSTACLE à False et TOURNER_EN_ROND à 0

  

Groupes de Neuones :  

Il y a plusieurs groupes de neurones pour contrôler les mouvements de l'hexapode :  

GControl : Groupe de neurones pour contrôler la direction (Reculer ou Avancer).  

GAv : Groupe de neurones pour contrôler l'avancement.  

GRe : Groupe de neurones pour contrôler le recul.  

GVitesseAvance : Groupe de neurones pour contrôler la vitesse sur GAv.  

GVitesseRecul : Groupe de neurones pour contrôler la vitesse sur GRe.  

GObstacleDevant, GObstacleDerriere, GObstacleDroite, GObstacleGauche : Groupes de neurones pour détecter les obstacles.  

  

Synapses  :
Il y a plusieurs synapses pour connecter les groupes de neurones :  

SControlAv : Synapses de contrôle pour l'avancement (entre GControl et GAv) 

SControlRe : Synapses de contrôle pour le recul.  (entre GControl et GRe) 

SInhib : Synapses pour inhiber GRe lors de l'action avancer (entre GAv et GRe) 

SVitesseAvance_cote_droit, SVitesseAvance_cote_gauche : Synapses pour contrôler la vitesse des pattes de droite ou de gauche lorsqu'on avance.  

SVitesseRecul_cote_droit, SVitesseRecul_cote_gauche : Synapses pour contrôler la vitesse des pattes de droite ou de gauche lorsqu'on recule.  

SObstacleDevantControl, SObstacledroite_GVitesseAvance, SObstacledroite_GVitesseRecule, SObstaclegauche_GVitesseAvance, SObstaclegauche_GVitesseRecule : Synapses pour gérer les obstacles.  

 

 
Run : 

Nous avons implémenté différents runs pour s’adapter aux changements de l'environnement et donc aux changements d’actions de l’hexapode.  

 