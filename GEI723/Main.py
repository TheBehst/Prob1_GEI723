from brian2 import *
import matplotlib.pyplot as plt
import math

############################### CHOIX UTILISATEURS ################################################

TURN = 0# 0 = STRAIGHT, 1 = LEFT, 2 = RIGHT    | NB: L'action de tourner commence des le debut
ACTION =2 #2 = AVANCER, 1 = RECULER
NB_PATTES = 6# doit etre pair et sup a 6
VITESSE =1 # 1 OU 2 POUR LE MOMENT
TOURNER_EN_ROND = 0#1=true, # on tourne en rond vers gauche en avancant

PRESCENCE_OBSTACLE = True

position= 1 # 1=avant ,2 = derriere,  3=droite, 4 = gauche
temps_apparition= 24 *ms # : temps d apparition de l obstacle  clem:69 behrouz:66
temps_action= 144 *ms #temps pour gerer l obstacle  clem:135 behrouz:198
#ratio_vitesse = 6/


# REGLES TEMPS D APPARITION et TEMPS ACTION
# obstacle devant : multiple de 6 

# obstacle heurte a droite en avancant: multiple de 6 + 3,  et temps d action k*3
# obstacle heurte a droite en reculant: multiple de 33 + 16.5, et temps d action + k*33 ex : 82.5 et 148.5

# obstacle heurte a gauche en avancant: multiple de 6 
# obstacle heurte a gauche en reculant: multiple de 33 




OBSTACLE = [None, None, None]
if PRESCENCE_OBSTACLE:
    OBSTACLE = [position, temps_apparition, temps_apparition+temps_action]#position doit etre coherent avec action

# Notes : 

#Note 1 :
#NB: L'action de tourner commence des que la variable TURN est changée

#Note 2 :
#TOURNER EN AVANCANT
# en supposant rayon de rotation a 0.2m, vlin = 0.1m/s, angle desire = 90deg, dilatation du temps avec facteur 83.33 pour faire correspondre 6ms a 500ms en realite
# On obtient que l'on souhaite faire 12 spikes de 0.3 sec pour tourner ( on double la vitesse d'un cote).

#TOURNER EN RECULANT
# en supposant rayon de rotation a 0.2m, vlin = 0.1m/s, angle desire = 90deg, dilatation du temps avec facteur 15.15 pour faire correspondre 33ms a 500ms en realite
# On obtient que l'on souhaite faire 12 spikes de 16.5 sec pour tourner, (  on double la vitesse d'un cote).


# VERIFICATION ET VALEURS PAR DEFAUT
if not (NB_PATTES > 0 and NB_PATTES % 2 == 0):
    NB_PATTES = 6

if ACTION not in [1, 2]:
    ACTION = 1

Text = "Avancer" if ACTION == 2 else "Reculer"

TextDirection = "en allant à gauche" if TURN == 1 else "en allant à droite" if TURN == 2 else "en tournant en rond" if TOURNER_EN_ROND== 1 else "sans tourner"

TexteObstacle = "à droite" if OBSTACLE [0]==3 else "devant" if OBSTACLE [0]==1  else "à gauche" if OBSTACLE [0]==4 else "derrière" if OBSTACLE [0]==2 else "Aucun"

#################################### DEF ##########################################

def delay_maker2(x1, x2, x3, x4, N):
    if N < 6 or N % 2 != 0:
        raise ValueError("N must be an even number greater than or equal to 6")

    list1 = [0] * N
    list2 = [0] * N

    for i in range(1, N, 4):  
        list1[i] = x2
    for i in range(2, N, 4):  
        list1[i] = x1

    for i in range(1, N, 4):  
        list2[i] = x4
    for i in range(2, N, 4):  
        list2[i] = x3

    return list1, list2

def delay_maker(N, start, delay):
    result = []
    for i in range(N):
        if i % 4 == 0 or i % 4 == 3:  
            result.append(start)
        else:  
            result.append(start + delay)
    return result

def delay_maker10(x1, x2, x3, x4, N):
    if N % 2 != 0:
        raise ValueError("N must be an even number.")
    
    list1 = [0, x1] * (N // 2)
    list2 = [x2, 0] * (N // 2)
    list3 = [0, x3] * (N // 2)
    list4 = [x4, 0] * (N // 2)
    
    return list1, list2, list3, list4

def odd_numbers(N):
    return [i for i in range(1, N+1, 2)]
def even_numbers(N):
    return [i for i in range(0, N, 2)]

def definir_temps(TURN, ACTION):
    t_start_base_av = 0* ms 
    t_end_base_av = 36* ms 
    t_start_base_re = 0* ms 
    t_end_base_re = 198* ms 
    
    dephase = 3 * ms if TURN == 1 and ACTION == 2 else 0
    dephase_re = 16.5 * ms if TURN == 1 and ACTION == 1 else 0
    
    if ACTION == 2 and TURN ==2 :  
        t_start_av = t_start_base_av + dephase
        t_end_av = t_end_base_av + dephase
        t_start_re = 0* ms 
        t_end_re = 0* ms 
    elif ACTION == 2 and TURN ==1 :  
        t_start_av = t_start_base_av + dephase
        t_end_av = t_end_base_av 
        t_start_re = 0* ms 
        t_end_re = 0* ms 
    elif ACTION == 1 and TURN == 2:  
        t_start_re = t_start_base_re + dephase_re
        t_end_re = t_end_base_re + dephase_re
        t_start_av = 0* ms 
        t_end_av = 0* ms 

    elif ACTION == 1 and TURN == 1:  
        t_start_re = t_start_base_re + dephase_re
        t_end_re = t_end_base_re 
        t_start_av = 0* ms 
        t_end_av = 0* ms 
    else:
        t_start_re = 0* ms 
        t_end_re = 0* ms 
        t_start_av = 0* ms 
        t_end_av = 0* ms 
    if TOURNER_EN_ROND ==1:
        t_end_av = t_end_base_av *4

    return t_start_av, t_end_av, t_start_re, t_end_re


def generate_alternative_list_moitie(num_pattes, weight1, weight2):# ex : (8,0.05, 0.06) = # [0.05, 0.06, 0.05, 0.06]

    base_weights = [weight1, weight2]

    weights = base_weights * (num_pattes // 2)  
    weights = weights[:len(weights) // 2]
    return weights



############################### VALEURS INITS ################################################


# definition des courants d entrees
# Pour la direction
LARGE_CURRENT = 2
SMALL_CURRENT = 1
Current = LARGE_CURRENT if ACTION == 2 else SMALL_CURRENT


#Pour tourner
CURRENT_TURN_AV = 5
CURRENT_TURN_RE = 5
Current_Turn_default = 0


Current_Turn_Av_Left = CURRENT_TURN_AV if TURN ==  1 and ACTION == 2 else Current_Turn_default
Current_Turn_Av_Right = CURRENT_TURN_AV if TURN ==  2  and ACTION == 2 else Current_Turn_default
Current_Turn_Re_Left = CURRENT_TURN_RE if TURN ==  1 and ACTION == 1 else Current_Turn_default
Current_Turn_Re_Right = CURRENT_TURN_RE if TURN ==  2  and ACTION == 1 else Current_Turn_default
Current_Turn_Av_Left = CURRENT_TURN_AV if ACTION == 2 and TOURNER_EN_ROND == 1 else Current_Turn_Av_Left

if VITESSE !=1:
    if ACTION ==2: 
        Current_Turn_Av_Left = CURRENT_TURN_AV*np.abs(VITESSE-1)
        Current_Turn_Av_Right = CURRENT_TURN_AV*np.abs(VITESSE-1)
    elif ACTION == 1:
        Current_Turn_Re_Left = CURRENT_TURN_RE*np.abs(VITESSE-1)
        Current_Turn_Re_Right = CURRENT_TURN_RE*np.abs(VITESSE-1)

# le temps pour lequel le neurone qui indique "tourne!" doit changer en fonction du cote comme il y a un dephasage
t_start_av, t_end_av, t_start_re, t_end_re = definir_temps(TURN, ACTION)
print("t_start_av:", t_start_av)
print("t_end_av:", t_end_av)
print("t_start_re:", t_start_re)
print("t_end_re:", t_end_re)

runtime = 72 if ACTION == 2 else 500



delais_av = 3 *ms
delais_re = 16.5 *ms
# OBSTACLE
CURRENT_OBSTACLE = 9
CURRENT_NO_OBSTACLE = 0

# devant
t_start_obstacle_devant = 0*ms
t_end_obstacle_devant  = 0*ms 
if PRESCENCE_OBSTACLE and OBSTACLE[0] == 1:
    t_start_obstacle_devant  = OBSTACLE[1]
    t_end_obstacle_devant  = OBSTACLE[2]  
print(f"\nt_start_obstacle_devant = {t_start_obstacle_devant}")
print(f"t_end_obstacle_devant = {t_end_obstacle_devant}")

# derriere
t_start_obstacle_derriere = 0*ms
t_end_obstacle_derriere  = 0*ms 
if PRESCENCE_OBSTACLE and OBSTACLE[0] == 2:
    t_start_obstacle_derriere  = OBSTACLE[1]
    t_end_obstacle_derriere  = OBSTACLE[2]  
print(f"\nt_start_obstacle_derriere = {t_start_obstacle_derriere}")
print(f"t_end_obstacle_derriere = {t_end_obstacle_derriere}")

# a droite
t_start_obstacle_droite = 0*ms
t_end_obstacle_droite  = 0*ms 
if PRESCENCE_OBSTACLE and OBSTACLE[0] == 3:
    t_start_obstacle_droite = OBSTACLE[1]
    t_end_obstacle_droite  = OBSTACLE[2]  

print(f"\nt_start_obstacle_droite = {t_start_obstacle_droite}")
print(f"t_end_obstacle_droite = {t_end_obstacle_droite}")

# a gauche

t_start_obstacle_gauche = 0*ms
t_end_obstacle_gauche  = 0*ms 
if PRESCENCE_OBSTACLE and OBSTACLE[0] == 4:
    t_start_obstacle_gauche = OBSTACLE[1]
    t_end_obstacle_gauche  = OBSTACLE[2]  

print(f"\nt_start_obstacle_gauche = {t_start_obstacle_gauche}")
print(f"t_end_obstacle_gauche = {t_end_obstacle_gauche}")

start_scope()

SeuilTourner = 0.1
seuilAv = 1
seuilRe = 0.5
seuilControle = 0.9
seuilObstacle = 1

eqs = """
dv/dt = (I-v) / tau : 1
tau : second
I : 1
spike_count : integer
t_start : second
t_end : second
"""


################################### GROUPES DE NEURONES ############################################

GControl = NeuronGroup(1, eqs, threshold='v>seuilControle', reset='v=0', method='euler')
GControl.tau = 1 * ms
GControl.I = Current


GAv = NeuronGroup(NB_PATTES, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GAv.tau = 10 * ms 

GRe = NeuronGroup(NB_PATTES, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GRe.tau = 500 * ms


GVitesseAvance = NeuronGroup(2, eqs, threshold='v>=SeuilTourner', reset='v=0', method='euler')# 2 neurones pour controler les 2 cotes des pattes séparément
GVitesseAvance.I = [Current_Turn_default, Current_Turn_default]
GVitesseAvance.tau = 10 * ms

GVitesseRecul = NeuronGroup(2, eqs, threshold='v>=SeuilTourner', reset='v=0', method='euler')
GVitesseRecul.I = [Current_Turn_default, Current_Turn_default]
GVitesseRecul.tau = 50* ms

GObstacleDevant = NeuronGroup(1, eqs, threshold='v>=seuilObstacle', reset='v=0', method='euler')
GObstacleDevant.I = CURRENT_NO_OBSTACLE   
GObstacleDevant.tau = 1 * ms 

GObstacleDerriere = NeuronGroup(1, eqs, threshold='v>=seuilObstacle', reset='v=0', method='euler')
GObstacleDerriere.I = CURRENT_NO_OBSTACLE  
GObstacleDerriere.tau = 0.1 * ms 

GObstacleDroite = NeuronGroup(2, eqs, threshold='v>=seuilObstacle', reset='v=0', method='euler')
GObstacleDroite.I = [CURRENT_NO_OBSTACLE , CURRENT_NO_OBSTACLE] 
GObstacleDroite.tau = 0.1 * ms 

GObstacleGauche = NeuronGroup(2, eqs, threshold='v>=seuilObstacle', reset='v=0', method='euler')
GObstacleGauche.I = [CURRENT_NO_OBSTACLE , CURRENT_NO_OBSTACLE] 
GObstacleGauche.tau = 0.1 * ms 


################################ SYNAPSES ###############################################


SControlAv = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w ')
SControlAv.connect(i=0, j=range(len(GAv)))  
SControlAv.w = '0.14'#6ms
SControlAv.delay = delay_maker(NB_PATTES,0,3/VITESSE)* ms 


# Synapses GControl -> GRe
SControlRe = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SControlRe.connect(i=0, j=range(len(GRe)))
SControlRe.w = '0.036'#33ms
SControlRe.delay = delay_maker(NB_PATTES,0, 16.5/VITESSE) * ms 
#SControlRe.delay = [0, 16.5,0,16.5, 0, 16.5] * ms

# Synapses GAv -> GRe pour inhiber
SInhib = Synapses(GAv, GRe, on_pre='v_post = 0')
SInhib.connect(condition='i==j')  

#Synapses pour aller a droite et a gauche en avancant

# DONE
SVitesseAvance_cote_droit = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_droit.connect(i=0, j = odd_numbers(NB_PATTES))
SVitesseAvance_cote_droit.w = generate_alternative_list_moitie(NB_PATTES, 0.05, 0.06)# car on veut delai entre spike de 3 sur neurone 3
SVitesseAvance_cote_droit.delay = generate_alternative_list_moitie(NB_PATTES, 3/VITESSE, 0)*ms# [3,0,3]*ms  neurone 1 a t=6 GOOD

# DONE
SVitesseAvance_cote_gauche = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_gauche.connect(i=1, j = even_numbers(NB_PATTES))
SVitesseAvance_cote_gauche.w = generate_alternative_list_moitie(NB_PATTES, 0.05, 0.06)#[0.05, 0.06, 0.05]#'0.06'#  car on veut delai entre spike de 3 sur neurone 2
SVitesseAvance_cote_gauche.delay = generate_alternative_list_moitie(NB_PATTES, 0, 3/VITESSE)*ms#[0,3,0]*ms# GOOD



# RECULER EN TOURNANT 
# #Synapses pour aller a droite et a gauche en reculant
SVitesseRecul_cote_droit = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_droit.connect(i=0, j = odd_numbers(NB_PATTES))#i=2?
SVitesseRecul_cote_droit.w = generate_alternative_list_moitie(NB_PATTES, 0.018, 0.018)##'0.018'car on veut delai entre spike de 16.5 sur neurone 3
#SVitesseRecul_cote_droit.delay = delay_maker(NB_PATTES,0, 8.25)[:NB_PATTES // 2] * ms#[16.5, 8.25, 16.5]  * ms
SVitesseRecul_cote_droit.delay = generate_alternative_list_moitie(NB_PATTES, 16.5/VITESSE, 0)*ms#[16.5,0,16.5]*ms# car on veut neurone 1 et 3 spike a t=33 GOOD

#DONE
SVitesseRecul_cote_gauche = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_gauche.connect(i=1, j = even_numbers(NB_PATTES))
SVitesseRecul_cote_gauche.w = generate_alternative_list_moitie(NB_PATTES, 0.018, 0.018)# '0.018' car on veut delai entre spike de 16.5 sur neurone 2
SVitesseRecul_cote_gauche.delay = generate_alternative_list_moitie(NB_PATTES, 0, 16.5/VITESSE)*ms#[0,16.5,0]*ms# car on veut neurone 2 spike a t=33 GOOD

# OBSTACLES

# # DEVANT
#SI il y a un obstacle devant : GControl passe de  "avance " à "recule"  
SObstacleDevantControl = Synapses(GObstacleDevant, GControl, 'w : 1', on_pre='v_post -= w')
SObstacleDevantControl.connect(i=0, j=0)  
SObstacleDevantControl.w = '0.24'# plus grand 0.235 = 2   on veut 2.2 ms``

# # SI il y a un obstacle devant : on stop les actions de tourner 
# # SObstacleDevant_GVitesseAvance = Synapses(GObstacleDevant, GVitesseAvance, 'w : 1', on_pre='v_post = w')
# # SObstacleDevant_GVitesseAvance.connect(i=0, j=range(len(GVitesseAvance)))  
# # SObstacleDevant_GVitesseAvance.w = '0'

# # # DERRIERE
SObstaclederriere_GVitesseAvance = Synapses(GObstacleDerriere, GAv, 'w : 1', on_pre='v_post += w')
SObstaclederriere_GVitesseAvance.connect(i=0, j=range(len(GAv)))  
SObstaclederriere_GVitesseAvance.w = '0.01' 

# # A DROITE

SObstacledroite_GVitesseAvance = Synapses(GObstacleDroite, GVitesseAvance, 'w : 1', on_pre='v_post += w')
SObstacledroite_GVitesseAvance.connect(i=0, j=0)
SObstacledroite_GVitesseAvance.w = '0.10'

SObstacledroite_GVitesseRecule= Synapses(GObstacleDroite, GVitesseRecul, 'w : 1', on_pre='v_post += w')
SObstacledroite_GVitesseRecule.connect(i=1, j=0)  
SObstacledroite_GVitesseRecule.w = '0.011' 


# # A GAUCHE
SObstaclegauche_GVitesseAvance = Synapses(GObstacleGauche, GVitesseAvance, 'w : 1', on_pre='v_post += w')
SObstaclegauche_GVitesseAvance.connect(i=0, j=1)  
SObstaclegauche_GVitesseAvance.w = '0.10' 

SObstaclegauche_GVitesseRecule= Synapses(GObstacleGauche, GVitesseRecul, 'w : 1', on_pre='v_post += w')
SObstaclegauche_GVitesseRecule.connect(i=1, j=1)  
SObstaclegauche_GVitesseRecule.w = '0.011' 



########################### NETWORK OPERATIONS ###########################

# @network_operation(dt=0.5*ms)
# def update_obstacle_droite():
#     if ACTION == 1:
#         if GObstacleDroite.t >= t_start_obstacle_droite and GObstacleDroite.t < t_end_obstacle_droite:
#             GObstacleDroite.I = [CURRENT_NO_OBSTACLE,CURRENT_OBSTACLE ]
#         if GObstacleDroite.t >= t_end_obstacle_droite:
#             GObstacleDroite.I = [CURRENT_NO_OBSTACLE ,CURRENT_NO_OBSTACLE]

########################### MONITOR ####################################

MControl = StateMonitor(GControl, 'v', record=True)
MAv = StateMonitor(GAv, 'v', record=True)
MRe = StateMonitor(GRe, 'v', record=True)
MVitesseAvance = StateMonitor(GVitesseAvance, 'v', record=True)
MVitesseRecul = StateMonitor(GVitesseRecul, 'v', record=True)
MObstacleDevant = StateMonitor(GObstacleDevant, 'v', record=True)
MObstacleDroite = StateMonitor(GObstacleDroite, 'v', record=True)
MObstacleGauche = StateMonitor(GObstacleGauche, 'v', record=True)


# Moniteur pour enregistrer les spikes des neurones
spike_monitor_ctrl = SpikeMonitor(GControl)
spike_monitor_re = SpikeMonitor(GRe)
spike_monitor_av = SpikeMonitor(GAv)
spike_monitor_CtrlVit_AV = SpikeMonitor(GVitesseAvance)
spike_monitor_CtrlVit_Re = SpikeMonitor(GVitesseRecul)
spike_monitor_Obst_devant = SpikeMonitor(GObstacleDevant)
spike_monitor_Obst_droite = SpikeMonitor(GObstacleDroite)
spike_monitor_Obst_gauche = SpikeMonitor(GObstacleGauche)




Run_time = runtime *ms
if TURN ==0 and OBSTACLE[0] ==None:
    Run_time = runtime/3 *ms

if TURN !=0 and ACTION == 2:
    Run_time = t_end_av

if TURN !=0 and ACTION == 1:
    Run_time = t_end_re

if OBSTACLE[0]==4:
    Run_time = t_start_obstacle_gauche
elif OBSTACLE[0]==3:
    GObstacleDroite.I = [CURRENT_NO_OBSTACLE ,CURRENT_NO_OBSTACLE]
    Run_time = t_start_obstacle_droite
elif OBSTACLE[0]==1:
    Run_time = t_start_obstacle_devant
elif OBSTACLE[0]==2:
    Run_time = t_start_obstacle_derriere

if TOURNER_EN_ROND==1:
    Run_time = t_end_av

#ajustement de vitesse

GVitesseAvance.I = [Current_Turn_Av_Left, Current_Turn_Av_Right]
GVitesseRecul.I = [Current_Turn_Re_Left, Current_Turn_Re_Right]

print(f'1111111111111111111 RUN time {Run_time}')
run(Run_time)


if VITESSE ==1:
    GVitesseAvance.I = [Current_Turn_default, Current_Turn_default] 
    GVitesseRecul.I = [Current_Turn_default, Current_Turn_default]
    if TURN ==0 and OBSTACLE[0] ==None:
        Run_time = runtime/3 *ms
    elif OBSTACLE[0]==4: #obstacle gauche
        Run_time = t_end_obstacle_gauche - t_start_obstacle_gauche
        if ACTION==2:
            GObstacleGauche.I = [CURRENT_OBSTACLE , CURRENT_NO_OBSTACLE]
        elif ACTION == 1:
            GObstacleGauche.I = [CURRENT_NO_OBSTACLE , CURRENT_OBSTACLE]
    elif OBSTACLE[0]==3: #obstacle droit
        Run_time = t_end_obstacle_droite - t_start_obstacle_droite
    elif OBSTACLE[0]==1: #obstacle devant
        Run_time = t_end_obstacle_devant - t_start_obstacle_devant
        SControlRe.delay = delay_maker(NB_PATTES,33,0)* ms #[0,33,33,0,0,33]* ms #delay_maker(NB_PATTES,0,0)* ms 
        GObstacleDevant.I = CURRENT_OBSTACLE
    elif OBSTACLE[0]==2: #obstacle derriere
        Run_time = t_end_obstacle_derriere - t_start_obstacle_derriere
        GObstacleDerriere.I = CURRENT_OBSTACLE
    if OBSTACLE[0] == 3:
        if ACTION==2:
            GObstacleDroite.I = [CURRENT_OBSTACLE , CURRENT_NO_OBSTACLE]
        elif ACTION == 1:
            GObstacleDroite.I = [CURRENT_NO_OBSTACLE , CURRENT_OBSTACLE]
    

        




print(f'GObstacleGauche.I {GObstacleGauche.I}')

print(f'22222222222222222 RUN time {Run_time}')

run(Run_time)

if TURN ==0 :
    Run_time = runtime/3 *ms

if OBSTACLE[0] !=None:
    Run_time = 24 *ms

if TURN !=0 :
    Run_time = 0 *ms

if OBSTACLE[0] == 3:
    GObstacleDroite.I = [CURRENT_NO_OBSTACLE ,CURRENT_NO_OBSTACLE]
if OBSTACLE[0] == 1:
    GObstacleDevant.I = CURRENT_NO_OBSTACLE
if OBSTACLE[0] == 2:
    GObstacleDerriere.I = CURRENT_NO_OBSTACLE
if OBSTACLE[0]==4:
    GObstacleGauche.I = [CURRENT_NO_OBSTACLE , CURRENT_NO_OBSTACLE]

print(f'333333333 RUN time {Run_time}')

run(Run_time)

# @network_operation(dt=0.1*ms) 
# def update_current():
#     if GVitesseAvance.t < t_end_av- 0.5*ms and GVitesseAvance.t >= t_start_av:
#         GVitesseAvance.I = [Current_Turn_Av_Left, Current_Turn_Av_Right, Current_vitesse]
       
#     if GVitesseAvance.t > t_end_av - 0.5*ms:
#         GVitesseAvance.I = [Current_Turn_default, Current_Turn_default, Current_vitesse]
    
#     if GVitesseRecul.t < t_end_re- 0.5*ms and GVitesseRecul.t >= t_start_re:
#         GVitesseRecul.I = [Current_Turn_Re_Left, Current_Turn_Re_Right, Current_vitesse]

 
#     if GVitesseRecul.t == t_end_re -0.5*ms:
#         GRe.v = [0,0,0,0,0,0]

#     if GVitesseRecul.t > t_end_re -0.5*ms:
#         GVitesseRecul.I = [Current_Turn_default, Current_Turn_default, Current_vitesse]

        

############################## AFTER RUN ################################################
# Control direction

spike_times_ctrl = spike_monitor_ctrl.spike_trains()[0]
delays_between_spikes_ctrl = diff(spike_times_ctrl)



#reculer
spike_times_neuron_0_re = spike_monitor_re.spike_trains()[0]
spike_times_neuron_1_re = spike_monitor_re.spike_trains()[1]
delays_between_spikes_0_re = diff(spike_times_neuron_0_re)
delays_between_spikes_1_re = diff(spike_times_neuron_1_re)

spike_times_neuron_2_re = spike_monitor_re.spike_trains()[2]
spike_times_neuron_3_re = spike_monitor_re.spike_trains()[3]
delays_between_spikes_2_re  = diff(spike_times_neuron_2_re)
delays_between_spikes_3_re  = diff(spike_times_neuron_3_re)

# avancer
spike_times_neuron_0_av = spike_monitor_av.spike_trains()[0]
spike_times_neuron_1_av = spike_monitor_av.spike_trains()[1]
delays_between_spikes_0_av = diff(spike_times_neuron_0_av)
delays_between_spikes_1_av = diff(spike_times_neuron_1_av)

spike_times_neuron_2_av = spike_monitor_av.spike_trains()[2]
spike_times_neuron_3_av = spike_monitor_av.spike_trains()[3]
delays_between_spikes_2_av  = diff(spike_times_neuron_2_av)
delays_between_spikes_3_av  = diff(spike_times_neuron_3_av)

# CTRL AV
spike_times_neuron_0_CtrlVit_AV = spike_monitor_CtrlVit_AV.spike_trains()[0]
spike_times_neuron_1_CtrlVit_AV = spike_monitor_CtrlVit_AV.spike_trains()[1]

delays_between_spikes_0_CtrlVit_AV  = diff(spike_times_neuron_0_CtrlVit_AV)
delays_between_spikes_1_CtrlVit_AV  = diff(spike_times_neuron_1_CtrlVit_AV)


# CTRL ARR

spike_times_neuron_0_CtrlVit_Re = spike_monitor_CtrlVit_Re.spike_trains()[0]
spike_times_neuron_1_CtrlVit_Re = spike_monitor_CtrlVit_Re.spike_trains()[1]
delays_between_spikes_0_CtrlVit_Re  = diff(spike_times_neuron_0_CtrlVit_Re)
delays_between_spikes_1_CtrlVit_Re  = diff(spike_times_neuron_1_CtrlVit_Re)

# obtacle devant

spike_times_obst_devant = spike_monitor_Obst_devant.spike_trains()[0]
delays_between_spikes_obst_devant = diff(spike_times_obst_devant)


# obtacle droite

spike_times_obst_droite = spike_monitor_Obst_droite.spike_trains()[0]
delays_between_spikes_obst_droite = diff(spike_times_obst_droite)


# obtacle gauche

spike_times_obst_gauche = spike_monitor_Obst_gauche.spike_trains()[0]
delays_between_spikes_obst_gauche = diff(spike_times_obst_gauche)

spike_times_obst_gauche_n1 = spike_monitor_Obst_gauche.spike_trains()[1]
delays_between_spikes_obst_gauche_n1 = diff(spike_times_obst_gauche_n1)

# Afficher les résultats
print(f"\n-------------------------------- CONTROL DIRECTION-------------------------------------------------------")

#print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0_re}")
print(f"Délais entre les spikes pour le CONTROL : {delays_between_spikes_ctrl}")

# Afficher les résultats
print(f"\n-------------------------------- OBSTACLE DEVANT -------------------------------------------------------")

#print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0_re}")
#print(f"Délais entre les spikes pour le OBSTACLE DEVANT : {delays_between_spikes_obst_devant}")


print(f"\n-------------------------------- RECULER -------------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0_re}")
print(f"Délais entre les spikes pour le neurone 0 : {delays_between_spikes_0_re}")
print(f"\nTemps de spikes pour le neurone 1 : {spike_times_neuron_1_re}")
print(f"Délais entre les spikes pour le neurone 1 : {delays_between_spikes_1_re}")

print(f"\nTemps de spikes pour le neurone 2(Reculer) : {spike_times_neuron_2_re}")
print(f"Délais entre les spikes pour le neurone 2 (Reculer) : {delays_between_spikes_2_re}")
print(f"\nTemps de spikes pour le neurone 3(Reculer) : {spike_times_neuron_3_re}")
print(f"Délais entre les spikes pour le neurone 3 (Reculer) : {delays_between_spikes_3_re}")
print(f"\n--------------------------------  AVANCER ------------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 (Avancer) : {spike_times_neuron_0_av}")
print(f"\nDélais entre les spikes pour le neurone 0 (Avancer) : {delays_between_spikes_0_av}")
print(f"\nTemps de spikes pour le neurone 1 (Avancer) : {spike_times_neuron_1_av}")
print(f"\nDélais entre les spikes pour le neurone 1 (Avancer) : {delays_between_spikes_1_av}")

print(f"\nTemps de spikes pour le neurone 2(Avancer) : {spike_times_neuron_2_av}")
print(f"Délais entre les spikes pour le neurone 2 (Avancer) : {delays_between_spikes_2_av}")
print(f"\nTemps de spikes pour le neurone 3(Avancer) : {spike_times_neuron_3_av}")
print(f"Délais entre les spikes pour le neurone 3 (Avancer) : {delays_between_spikes_3_av}")


print(f"\n---------------------------------- CTRLVIT_AV -----------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 (CtrlVit_AV) : {spike_times_neuron_0_CtrlVit_AV}")
print(f"Délais entre les spikes pour le neurone 0 (CtrlVit_AV) : {delays_between_spikes_0_CtrlVit_AV}")
print(f"Temps de spikes pour le neurone 1 (CtrlVit_AV) : {spike_times_neuron_1_CtrlVit_AV}")
print(f"Délais entre les spikes pour le neurone 1 (CtrlVit_AV) : {delays_between_spikes_1_CtrlVit_AV}")

print(f"\n-------------------------------- OBSTACLE GAUCHE -------------------------------------------------------")

#print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0_re}")
print(f"Délais entre les spikes pour le OBSTACLE GAUCHE 0: {delays_between_spikes_obst_gauche}")
print(f"Délais entre les spikes pour le OBSTACLE GAUCHE 1 : {delays_between_spikes_obst_gauche_n1}")


print(f"\n-------------------------------- OBSTACLE DROITE -------------------------------------------------------")

#print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0_re}")
print(f"Délais entre les spikes pour le OBSTACLE DROITE : {delays_between_spikes_obst_droite}")

print(f"\n---------------------------------- CTRLVIT_Re -----------------------------------------------------")

# print(f"Temps de spikes pour le neurone 0 (CtrlVit_Re) : {spike_times_neuron_0_CtrlVit_Re}")
# print(f"Délais entre les spikes pour le neurone 0 (CtrlVit_Re) : {delays_between_spikes_0_CtrlVit_Re}")
# print(f"Temps de spikes pour le neurone 1 (CtrlVit_Re) : {spike_times_neuron_1_CtrlVit_Re}")
# print(f"Délais entre les spikes pour le neurone 1 (CtrlVit_Re) : {delays_between_spikes_1_CtrlVit_Re}")
##############################################################################

# Visualiser les résultats
nbfig = 2
i=0
if TURN !=0 or OBSTACLE[0]!= None:
    nbfig = 3

fig1, axes = plt.subplots(nbfig , 1, sharex=True)
if OBSTACLE[1] != None:
    fig1.suptitle(f'{Text} en allant {TextDirection}, obstacle ({TexteObstacle} de {OBSTACLE[1]} à {OBSTACLE[2]})', fontsize=16)
else:
    fig1.suptitle(f'{Text} en allant {TextDirection}', fontsize=16)


# ax = axes[0]
# ax.plot(MControl.t/ms, MControl.v[0], color='blue')
# ax.axhline(y=seuilControle, ls='--', color='g')
# ax.set_ylabel('Potentiel')
# ax.set_title(f'Neurone de controle de direction  avec courant pour {Text} ')

# ax = axes[0]
# ax.plot(MObstacleDevant.t/ms, MObstacleDevant.v[0], color='blue')
# ax.axhline(y=seuilObstacle, ls='--', color='g')
# ax.set_ylabel('Potentiel')
# ax.set_title(f'Neurone de obstacle devant')

# ax = axes[0]
# ax.plot(MObstacleDroite.t/ms, MObstacleDroite.v[0], color='blue')
# ax.axhline(y=seuilObstacle, ls='--', color='g')
# ax.set_ylabel('Potentiel')
# ax.set_title(f'Neurone de obstacle droite  ( de {OBSTACLE[1]} a {OBSTACLE[2]} ) ')

# ax = axes[0]
# ax.plot(MObstacleGauche.t/ms, MObstacleGauche.v[0], color='blue')
# ax.axhline(y=seuilObstacle, ls='--', color='g')
# ax.set_ylabel('Potentiel')
# ax.set_title(f'Neurone de obstacle Gauche ')

ax = axes[i]
ax.plot(MAv.t/ms, MAv.v[0], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone 0 Avancer (PATTES DE GAUCHE)')

ax = axes[i+1]
ax.plot(MRe.t/ms, MRe.v[0], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 Reculer (PATTES DE GAUCHE)')

if (ACTION ==2 and TURN !=0) or (OBSTACLE[0]!= 1 and OBSTACLE[0]!= None) :
    ax = axes[i+2]
    ax.plot(MVitesseAvance.t/ms, MVitesseAvance.v[1], color='blue')
    ax.axhline(y=SeuilTourner, ls='--', color='g')
    ax.set_ylabel('Potentiel')
    ax.set_xlabel('Temps (ms)')
    ax.set_title('Neurone 1 du controle de vitesse en avancant')

if (ACTION ==1 and TURN !=0) :
    ax = axes[i+2]
    ax.plot(MVitesseRecul.t/ms, MVitesseRecul.v[1], color='grey')
    ax.axhline(y=SeuilTourner, ls='--', color='g')
    ax.set_ylabel('Potentiel')
    ax.set_xlabel('Temps (ms)')
    ax.set_title('Neurone 1 du controle de vitesse en reculant')

fig1.tight_layout()  
fig1.subplots_adjust(hspace=0.7)  



i=0
fig2, axes = plt.subplots(nbfig, 1, sharex=True)

if OBSTACLE[1] != None:
    fig2.suptitle(f'{Text} en allant {TextDirection}, obstacle ({TexteObstacle} de {OBSTACLE[1]} à {OBSTACLE[2]})', fontsize=16)
else:
    fig2.suptitle(f'{Text} en allant {TextDirection}', fontsize=16)




# ax = axes[0]
# ax.plot(MControl.t/ms, MControl.v[0], color='blue')
# ax.axhline(y=seuilControle, ls='--', color='g')
# ax.set_ylabel('Potentiel')
# ax.set_title(f'Neurone controle de direction avec courant pour {Text} ')

ax = axes[i]
ax.plot(MAv.t/ms, MAv.v[1], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone 1 Avancer (PATTES DE DROITE)')

ax = axes[i+1]
ax.plot(MRe.t/ms, MRe.v[1], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 1 Reculer (PATTES DE DROITE)')
if ( ACTION ==2 and TURN !=0 ) or (OBSTACLE[0]!= 1 and OBSTACLE[0]!= None):

    ax = axes[i+2]
    ax.plot(MVitesseAvance.t/ms, MVitesseAvance.v[0], color='blue')
    ax.axhline(y=SeuilTourner, ls='--', color='g')
    ax.set_ylabel('Potentiel')
    ax.set_xlabel('Temps (ms)')
    ax.set_title('Neurone 0 du controle de vitesse en avancant')
if (ACTION ==1 and TURN !=0) :

    ax = axes[i+2]
    ax.plot(MVitesseRecul.t/ms, MVitesseRecul.v[0], color='grey')
    ax.axhline(y=SeuilTourner, ls='--', color='g')
    ax.set_ylabel('Potentiel')
    ax.set_xlabel('Temps (ms)')
    ax.set_title('Neurone 0 du controle de vitesse en reculant')



fig2.tight_layout()  # Ajuste les limites de la figure
fig2.subplots_adjust(hspace=0.7)  # Ajuste l'espacement vertical entre les sous-graphes



# fig3, axes = plt.subplots(NB_PATTES, 1, sharex=True)
# for i in range(NB_PATTES):
#     ax = axes[i]
#     ax.plot(MAv.t/ms, MAv.v[i], color='orange')
#     ax.axhline(y=seuilAv, ls='--', color='g')
#     ax.set_ylabel('Potentiel')
#     ax.set_title(f'Neurone {i} Avancer')

########### OU
if TURN ==0 and ACTION == 2 and OBSTACLE[0]==None and TOURNER_EN_ROND==0:

    fig3, axes = plt.subplots(3, 1, sharex=True)  
    fig3.suptitle(f'Groupe de Neurones Avancer, vitesse = {VITESSE}', fontsize=16)

    ax_group1 = axes[0]  
    ax_group2 = axes[1]  
    ax_superposition = axes[2]  

    colors_spectre = plt.cm.viridis(np.linspace(0, 1, NB_PATTES))


    group1_indices = [i for i in range(NB_PATTES) if i % 4 == 0 or i % 4 == 3]
    group2_indices = [i for i in range(NB_PATTES) if i % 4 == 1 or i % 4 == 2]

    
    for i in group1_indices:
        ax_group1.plot(MAv.t/ms, MAv.v[i], color=colors_spectre[i], label=f'Neurone {i} Avancer')
    ax_group1.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
    ax_group1.legend(loc='upper right')

    for i in group2_indices:
        ax_group2.plot(MAv.t/ms, MAv.v[i], color=colors_spectre[i], label=f'Neurone {i} Avancer')
    ax_group2.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
    ax_group2.legend(loc='upper right')

    ax_superposition.plot(MAv.t/ms, MAv.v[0], color='blue', label='Neurone 0 Avancer')
    ax_superposition.plot(MAv.t/ms, MAv.v[1], color='orange', label='Neurone 1 Avancer')
    ax_superposition.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
    ax_superposition.legend(loc='upper right')

    ax_group1.set_ylabel('Potentiel')
    ax_group1.set_title('Neurones sans phase')

    ax_group2.set_ylabel('Potentiel')
    ax_group2.set_title('Neurones avec phase')

    ax_superposition.set_ylabel('Potentiel')
    ax_superposition.set_title('Superposition des Neurones 0 et 1')

    axes[-1].set_xlabel('Temps (ms)')
    fig3.subplots_adjust(hspace=0.4)


if (TURN !=0 and ACTION == 2) or OBSTACLE[0]!=None or TOURNER_EN_ROND==1:
    fig3, axes = plt.subplots(4, 1, sharex=True)  
    fig3.suptitle('Groupe de Neurones Avancer', fontsize=16)

    ax_right = axes[0]  
    ax_left = axes[1]  
    ax_without_phase = axes[2]  
    ax_with_phase = axes[3]  

    colors_spectre = plt.cm.viridis(np.linspace(0, 1, NB_PATTES))

    right_indices = [i for i in range(NB_PATTES) if i % 2 != 0]
    left_indices = [i for i in range(NB_PATTES) if i % 2 == 0]

    for i in right_indices:
        ax_right.plot(MAv.t/ms, MAv.v[i], color=colors_spectre[i], label=f'Neurone {i} Avancer')
    ax_right.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
    ax_right.legend(loc='upper right')

    for i in left_indices:
        ax_left.plot(MAv.t/ms, MAv.v[i], color=colors_spectre[i], label=f'Neurone {i} Avancer')
    ax_left.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
    ax_left.legend(loc='upper right')

    without_phase_indices = [i for i in range(NB_PATTES) if i % 4 == 0 or i % 4 == 3]

    for i in without_phase_indices:
        ax_without_phase.plot(MAv.t/ms, MAv.v[i], color=colors_spectre[i], label=f'Neurone {i} Avancer')
    ax_without_phase.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
    ax_without_phase.legend(loc='upper right')

    with_phase_indices = [i for i in range(NB_PATTES) if i % 4 == 1 or i % 4 == 2]

    for i in with_phase_indices:
        ax_with_phase.plot(MAv.t/ms, MAv.v[i], color=colors_spectre[i], label=f'Neurone {i} Avancer')
    ax_with_phase.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
    ax_with_phase.legend(loc='upper right')

    ax_right.set_ylabel('Potentiel')
    ax_right.set_title('Neurones des pattes de droite')

    ax_left.set_ylabel('Potentiel')
    ax_left.set_title('Neurones des pattes de gauche')

    ax_without_phase.set_ylabel('Potentiel')
    ax_without_phase.set_title('Neurones sans phase')

    ax_with_phase.set_ylabel('Potentiel')
    ax_with_phase.set_title('Neurones avec phase')

    axes[-1].set_xlabel('Temps (ms)')
    fig3.subplots_adjust(hspace=0.4)


#### VERIFIER LE BON DEPHASE DES PATTES POUR LE GROUPE RECULER  ####            NE PAS SUPPRIMER

# fig4, axes = plt.subplots(NB_PATTES, 1, sharex=True)
# for i in range(NB_PATTES):
#     ax = axes[i]
#     ax.plot(MRe.t/ms, MRe.v[i], color='red')
#     ax.axhline(y=seuilRe, ls='--', color='g')
#     ax.set_ylabel('Potentiel')
#     ax.set_title(f'Neurone {i} Reculer')

# fig4.tight_layout()

######################### OU

# DANS LE CAS AVANCE OU RECULE SANS TOURNER

if TURN ==0 and ACTION == 1:

    fig4, axes = plt.subplots(3, 1, sharex=True)
    fig4.suptitle('Groupe de Neurones Reculer', fontsize=16)

    ax_group1 = axes[0]  
    ax_group2 = axes[1]  
    ax_superposition = axes[2]  

    colors_spectre = plt.cm.viridis(np.linspace(0, 1, NB_PATTES))

    group1_indices = [i for i in range(NB_PATTES) if i % 4 == 0 or i % 4 == 3]
    group2_indices = [i for i in range(NB_PATTES) if i % 4 == 1 or i % 4 == 2]

    for i in group1_indices:
        ax_group1.plot(MRe.t/ms, MRe.v[i], color=colors_spectre[i], label=f'Neurone {i} Reculer')
    ax_group1.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
    ax_group1.legend(loc='upper right')

    for i in group2_indices:
        ax_group2.plot(MRe.t/ms, MRe.v[i], color=colors_spectre[i], label=f'Neurone {i} Reculer')
    ax_group2.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
    ax_group2.legend(loc='upper right')

    ax_superposition.plot(MRe.t/ms, MRe.v[0], color='blue', label='Neurone 0 Reculer')
    ax_superposition.plot(MRe.t/ms, MRe.v[1], color='orange', label='Neurone 1 Reculer')
    ax_superposition.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
    ax_superposition.legend(loc='upper right')

    ax_group1.set_ylabel('Potentiel')
    ax_group1.set_title('Neurones sans phase')

    ax_group2.set_ylabel('Potentiel')
    ax_group2.set_title('Neurones avec phase')

    ax_superposition.set_ylabel('Potentiel')
    ax_superposition.set_title('Superposition des Neurones 0 et 1')

    axes[-1].set_xlabel('Temps (ms)')


# DANS LE CAS AVANCE OU RECULE AVEC TOURNER
if (TURN !=0 and ACTION == 1) or OBSTACLE[0]==1:
    fig4, axes = plt.subplots(4, 1, sharex=True)  
    fig4.suptitle('Groupe de Neurones Reculer', fontsize=16)

    ax_group1 = axes[0]  
    ax_group2 = axes[1]
    ax_without_phase_re = axes[2]  
    ax_with_phase_re = axes[3]     

    colors_spectre = plt.cm.viridis(np.linspace(0, 1, NB_PATTES))

    group1_indices = [i for i in range(NB_PATTES) if i % 2 == 0]  
    group2_indices = [i for i in range(NB_PATTES) if i % 2 == 1]  

    for i in group1_indices:
        ax_group1.plot(MRe.t/ms, MRe.v[i], color=colors_spectre[i], label=f'Neurone {i} Reculer')
    ax_group1.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
    ax_group1.legend(loc='upper right')
    ax_group1.set_ylabel('Potentiel')
    ax_group1.set_title('Pattes de droite')

    for i in group2_indices:
        ax_group2.plot(MRe.t/ms, MRe.v[i], color=colors_spectre[i], label=f'Neurone {i} Reculer')
    ax_group2.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
    ax_group2.legend(loc='upper right')
    ax_group2.set_ylabel('Potentiel')
    ax_group2.set_title('Pattes de gauche')

    without_phase_indices_re = [i for i in range(NB_PATTES) if i % 4 == 0 or i % 4 == 3]
    for i in without_phase_indices_re:
        ax_without_phase_re.plot(MRe.t/ms, MRe.v[i], color=colors_spectre[i], label=f'Neurone {i} Reculer')
    ax_without_phase_re.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
    ax_without_phase_re.legend(loc='upper right')
    ax_without_phase_re.set_ylabel('Potentiel')
    ax_without_phase_re.set_title('Neurones sans phase')

    with_phase_indices_re = [i for i in range(NB_PATTES) if i % 4 == 1 or i % 4 == 2]
    for i in with_phase_indices_re:
        ax_with_phase_re.plot(MRe.t/ms, MRe.v[i], color=colors_spectre[i], label=f'Neurone {i} Reculer')
    ax_with_phase_re.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
    ax_with_phase_re.legend(loc='upper right')
    ax_with_phase_re.set_ylabel('Potentiel')
    ax_with_phase_re.set_title('Neurones avec phase')

    axes[-1].set_xlabel('Temps (ms)')
    fig4.subplots_adjust(hspace=0.4)



def visualise_connectivity(S):
    Ns = len(S.source)
    Nt = len(S.target)

    figure(figsize=(10, 4))

    subplot(121)
    plot(zeros(Ns), arange(Ns), 'ok', ms=10)
    plot(ones(Nt), arange(Nt), 'ok', ms=10)
    for i, j in zip(S.i, S.j):
        plot([0, 1], [i, j], '-k')
    xticks([0, 1], ['Source', 'Cible'])
    ylabel('Indice du neurone')
    xlim(-0.1, 1.1)
    ylim(-1, max(Ns, Nt))

    subplot(122)
    plot(S.i, S.j, 'ok')
    xlim(-1, Ns)
    ylim(-1, Nt)
    xlabel('Indice du neurone source')
    ylabel('Indice du neurone cible')



#visualise_connectivity(SInhib)
#visualise_connectivity(SVitesseAvance_cote_gauche)
#visualise_connectivity(SVitesseAvance_cote_droit)
#visualise_connectivity(SVitesseRecul_cote_gauche)
#visualise_connectivity(SVitesseRecul_cote_droit)
plt.show()
