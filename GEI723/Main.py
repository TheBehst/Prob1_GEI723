from brian2 import *
import matplotlib.pyplot as plt
import math

############################### 4 CHOIX UTILISATEURS ################################################

TURN =0# 0 = STRAIGHT, 1 = LEFT, 2 = RIGHT    | NB: L'action de tourner commence des le debut
ACTION = 2#2 = AVANCER, 1 = RECULER
NB_PATTES = 6 # doit etre pair
VITESSE = 1 #

PRESCENCE_OBSTACLE = False

position= 3 # 1=avant , 3=droite, 4 = gauche
temps_apparition= 69 *ms # : temps d apparition de l obstacle
temps_action= 135 *ms #temps pour gerer l obstacle

# REGLES TEMPS D APPARITION et TEMPS ACTION
# obstacle devant : multiple de 6 , NB il y aura tj un pb sur le 1er spike du neurone 1 reculer, voir Note 3

# obstacle heurte a droite en avancant: multiple de 6 + 3,  et temps d action k*3
# obstacle heurte a droite en reculant: multiple de 33 + 16.5, et temps d action + k*33 ex : 82.5 et 148.5

# obstacle heurte a gauche en avancant: multiple de 6 
# obstacle heurte a gauche en reculant: multiple de 33 


# TODO VERIFER LE BON DEPHASAGE DES PATTES DS CHACUN DES CAS


OBSTACLE = [None, None, None]
if PRESCENCE_OBSTACLE:
    OBSTACLE = [position, temps_apparition, temps_apparition+temps_action]#position doit etre coherent avec action
#VITESSE = 1 #

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

#Note 3 :
# OBSTACLE EN AVANCANT
# Pour le neurone 1, le dephasage n est pas respecte pour le 1er spike car l'obstacle est decouvert lorsque les neurones sont a moite charges :
# ( si on regarde le moment ou le neurone de controle change de courant pour passer de "avancer" a "reculer" + delai de propagation : on observe le moment ou l impact du changement se fait sentir sur les pattes). 
# et comme il y a toujours un dephasage entre les pattes gauches et les pattes droites,
# on ne pourra jamais faire en sorte que l 'obstacle soit decouvert lorsque les neurones sont dechargés (PM a 0) sur les pattes droite ET gauche.
# SAUF SI ON FAIT 2 NEURONES DANS OBSTACLE DEVANT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# VERIFICATION ET VALEURS PAR DEFAUT
if not (NB_PATTES > 0 and NB_PATTES % 2 == 0):
    NB_PATTES = 6

if ACTION not in [1, 2]:
    ACTION = 1

Text = "Avancer" if ACTION == 2 else "Reculer"
TextDirection = "à gauche" if TURN == 1 else "à droite" if TURN == 2 else "sans tourner"
TexteObstacle = "à droite" if OBSTACLE [0]==3 else "devant" if OBSTACLE [0]==1  else "à gauche" if OBSTACLE [0]==4 else "Aucun"

#################################### DEF ##########################################
def calculate_spike_cycle_period_with_spikes(input_spike_periods, input_weights, threshold, tau, v_init=0):
     # Calculate the input contributions from each neuron over one spike cycle
    input_contributions = [
        weight * (1 - np.exp(-period / tau)) 
        for weight, period in zip(input_weights, input_spike_periods)
    ]
    
    # Sum the contributions from all inputs
    total_input_per_cycle = sum(input_contributions)

    if total_input_per_cycle <= 0:
        raise ValueError("Total input is insufficient to reach the threshold.")
    
    # Calculate how many cycles it takes for the target neuron to reach its threshold
    cycles_to_threshold = (threshold - v_init) / total_input_per_cycle
    
    # The total spike cycle period is the average of the input spike periods multiplied by the number of cycles
    avg_input_period = sum(input_spike_periods) / len(input_spike_periods)
    spike_cycle_period = cycles_to_threshold * avg_input_period

    return spike_cycle_period


def calculate_spike_period_with_I(I, tau, threshold, reset_value, v_init=0):

    if isinstance(tau, Quantity):
        tau = tau.item()  # Extracts the scalar value of the quantity (in base units, e.g., seconds)

    if I <= threshold:
        # If input current is not enough to reach the threshold, the neuron won't spike
        return 0
    
    # Calculate the time it takes to reach the threshold
    time_to_spike = -tau * np.log((threshold - I) / (v_init - I))
    
    # Calculate the time it takes to reset
    time_to_reset = -tau * np.log((reset_value - I) / (v_init - I))
    
    # Total time for one spike cycle (spike + reset)
    total_spike_cycle_time = time_to_spike + time_to_reset
    
    return total_spike_cycle_time

def gestionnaire_delais(SVitesseAvance_w, SControlAv_w, SControlRe_w, SVitesseAvance_cote_gauche_w, SVitesseRecul_cote_droit_w, GVitesseAvance_I,
                        GControl_I, GVitesseRecul_I, GControl_tau, GVitesseAvance_tau,  GVitesseRecul_tau, GAv_tau, GRe_tau):
    weightsAv = [float(SVitesseAvance_w[0]), float(SControlAv_w[0]),  float(SVitesseAvance_cote_gauche_w[0])]
    weightsRe = [float(SVitesseAvance_w[0]), float(SControlRe_w[0]), float(SVitesseRecul_cote_droit_w[0])]
    T_spikes_recu_AvDr = [float(calculate_spike_period_with_I(GVitesseAvance_I[2], GVitesseAvance_tau, SeuilTourner, 0, 0) / ms),
                    float(calculate_spike_period_with_I(GControl_I, GControl_tau, seuilControle, 0, 0) / ms),
                    float(calculate_spike_period_with_I(GVitesseAvance_I[0], GVitesseAvance_tau, SeuilTourner, 0, 0) / ms)]
    T_spikes_recu_AvG = [float(calculate_spike_period_with_I(GVitesseAvance_I[2], GVitesseAvance_tau, SeuilTourner, 0, 0) / ms),
                    float(calculate_spike_period_with_I(GControl_I, GControl_tau, seuilControle, 0, 0) / ms),
                    float(calculate_spike_period_with_I(GVitesseAvance_I[1], GVitesseAvance_tau, SeuilTourner, 0, 0) / ms)]
    T_spikes_recu_ReDr = [float(calculate_spike_period_with_I(GVitesseRecul_I[2], GVitesseRecul_tau, SeuilTourner, 0, 0) / ms),
                    float(calculate_spike_period_with_I(GControl_I, GControl_tau, seuilControle, 0, 0) / ms),
                    float(calculate_spike_period_with_I(GVitesseRecul_I[0], GVitesseRecul_tau, SeuilTourner, 0, 0) / ms)]
    T_spikes_recu_ReG = [float(calculate_spike_period_with_I(GVitesseRecul_I[2], GVitesseRecul_tau, SeuilTourner, 0, 0) / ms),
                    float(calculate_spike_period_with_I(GControl_I, GControl_tau, seuilControle, 0, 0) / ms),
                    float(calculate_spike_period_with_I(GVitesseRecul_I[1], GVitesseRecul_tau, SeuilTourner, 0, 0) / ms)]
    T_spike_avancer_droit = calculate_spike_cycle_period_with_spikes(T_spikes_recu_AvDr, weightsAv, seuilAv, GAv_tau)
    T_spike_avancer_gauche = calculate_spike_cycle_period_with_spikes(T_spikes_recu_AvG, weightsAv, seuilAv, GAv_tau)
    T_spike_reculer_droit = calculate_spike_cycle_period_with_spikes(T_spikes_recu_ReDr, weightsRe, seuilRe, GRe_tau)
    T_spike_reculer_gauche = calculate_spike_cycle_period_with_spikes(T_spikes_recu_ReG, weightsRe, seuilRe, GRe_tau)
    return delay_maker2(T_spike_avancer_droit/2, T_spike_avancer_gauche/2, T_spike_reculer_droit, T_spike_reculer_gauche, NB_PATTES)

def delay_maker2(x1, x2, x3, x4, N):
    if N < 6 or N % 2 != 0:
        raise ValueError("N must be an even number greater than or equal to 6")

    list1 = [0] * N
    list2 = [0] * N

    # Fill list1: even indices alternate between 0 and x1, odd indices alternate between x2 and 0
    for i in range(1, N, 4):  # Odd indices for list1 get x2
        list1[i] = x2
    for i in range(2, N, 4):  # Even indices for list1 get x1
        list1[i] = x1

    # Fill list2: even indices alternate between 0 and x3, odd indices alternate between x4 and 0
    for i in range(1, N, 4):  # Odd indices for list2 get x4
        list2[i] = x4
    for i in range(2, N, 4):  # Even indices for list2 get x3
        list2[i] = x3

    return list1, list2


def delay_maker(N, start, delay):
    result = []
    for i in range(N):
        if i % 2 == 0 :  
            result.append(start)
        else:  
            result.append(start + delay)
    return result

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
    
    if ACTION == 2 and TURN != 0:  
        t_start_av = t_start_base_av + dephase
        t_end_av = t_end_base_av + dephase
        t_start_re = 0* ms 
        t_end_re = 0* ms 
    elif ACTION == 1 and TURN != 0:  
        t_start_re = t_start_base_re + dephase_re
        t_end_re = t_end_base_re + dephase_re
        t_start_av = 0* ms 
        t_end_av = 0* ms 
    else:
        t_start_re = 0* ms 
        t_end_re = 0* ms 
        t_start_av = 0* ms 
        t_end_av = 0* ms 

    return t_start_av, t_end_av, t_start_re, t_end_re
############################### VALEURS INITS ################################################


# definition des courants d entrees
# Pour la direction
LARGE_CURRENT = 2
SMALL_CURRENT = 1
CURRENTS_VITESSE = [0, 0.2, 0.4]
Current_vitesse = CURRENTS_VITESSE[VITESSE-1]
Current = LARGE_CURRENT if ACTION == 2 else SMALL_CURRENT

#Pour tourner
CURRENT_TURN_AV = 5
CURRENT_TURN_RE = 5
Current_Turn_default = 0

Current_Turn_Av_Left = CURRENT_TURN_AV if TURN ==  1 and ACTION == 2 else Current_Turn_default
Current_Turn_Av_Right = CURRENT_TURN_AV if TURN ==  2  and ACTION == 2 else Current_Turn_default
Current_Turn_Re_Left = CURRENT_TURN_RE if TURN ==  1 and ACTION == 1 else Current_Turn_default
Current_Turn_Re_Right = CURRENT_TURN_RE if TURN ==  2  and ACTION == 1 else Current_Turn_default

# le temps pour lequel le neurone qui indique "tourne!" doit changer en fonction du cote comme il y a un dephasage
t_start_av, t_end_av, t_start_re, t_end_re = definir_temps(TURN, ACTION)
# print(f"Avancer: t_start_av = {t_start_av}, t_end_av = {t_end_av}")
# print(f"Reculer: t_start_re = {t_start_re}, t_end_re = {t_end_re}")


# OBSTACLE
CURRENT_OBSTACLE = 9
CURRENT_NO_OBSTACLE = 0

# devant
t_start_obstacle_devant = 0*ms
t_end_obstacle_devant  = 0*ms 
if PRESCENCE_OBSTACLE and OBSTACLE[0] == 1:
    t_start_obstacle_devant  = OBSTACLE[1]
    t_end_obstacle_devant  = OBSTACLE[2]  

# a droite
t_start_obstacle_droite = 0*ms
t_end_obstacle_droite  = 0*ms 
if PRESCENCE_OBSTACLE and OBSTACLE[0] == 3:
    t_start_obstacle_droite = OBSTACLE[1]
    t_end_obstacle_droite  = OBSTACLE[2]  


# a gauche

t_start_obstacle_gauche = 0*ms
t_end_obstacle_gauche  = 0*ms 
if PRESCENCE_OBSTACLE and OBSTACLE[0] == 4:
    t_start_obstacle_gauche = OBSTACLE[1]
    t_end_obstacle_gauche  = OBSTACLE[2]  

print(f"t_start_obstacle_gauche = {t_start_obstacle_gauche}")
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
threshold : 1
reset : 1
"""


################################### GROUPES DE NEURONES ############################################

GControl = NeuronGroup(1, eqs, threshold='v>seuilControle', reset='v=0', method='euler')
GControl.tau = 1 * ms
GControl.I = Current

GAv = NeuronGroup(NB_PATTES, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GAv.tau = 10 * ms 
group_1_indices = []
group_2_indices = []

# # Generalize the assignment of thresholds based on neuron indices
# for i in range(NB_PATTES):
#     if (i % 6) in [0, 3, 4]:  # Neurons for Group 1 (0, 3, 4, 7, ...)
#         group_1_indices.append(i)
#     else:  # Neurons for Group 2 (1, 2, 5, 6, ...)
#         group_2_indices.append(i)

# # Assign thresholds to the respective groups

# GAv.v[group_1_indices] = 0
# GAv.v[group_2_indices] = 0

GRe = NeuronGroup(NB_PATTES, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GRe.tau = 500 * ms
GRe.v[group_1_indices] = 0
GRe.v[group_2_indices] = 0

GVitesseAvance = NeuronGroup(3, eqs, threshold='v>=SeuilTourner', reset='v=0', method='euler')# 2 neurones pour controler les 2 cotes des pattes séparément
GVitesseAvance.I = [Current_Turn_default, Current_Turn_default, Current_vitesse]
GVitesseAvance.tau = 10 * ms

GVitesseRecul = NeuronGroup(3, eqs, threshold='v>=SeuilTourner', reset='v=0', method='euler')
GVitesseRecul.I = [Current_Turn_default, Current_Turn_default, Current_vitesse]
GVitesseRecul.tau = 50* ms

GObstacleDevant = NeuronGroup(1, eqs, threshold='v>=seuilObstacle', reset='v=0', method='euler')
GObstacleDevant.I = CURRENT_NO_OBSTACLE   
GObstacleDevant.tau = 1 * ms 

GObstacleDroite = NeuronGroup(2, eqs, threshold='v>=seuilObstacle', reset='v=0', method='euler')
GObstacleDroite.I = [CURRENT_NO_OBSTACLE , CURRENT_NO_OBSTACLE] 
GObstacleDroite.tau = 0.1 * ms 

GObstacleGauche = NeuronGroup(2, eqs, threshold='v>=seuilObstacle', reset='v=0', method='euler')
GObstacleGauche.I = [CURRENT_NO_OBSTACLE , CURRENT_NO_OBSTACLE] 
GObstacleGauche.tau = 0.1 * ms 


################################ SYNAPSES ###############################################


SControlAv = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w')
SControlAv.connect(i=0, j=range(len(GAv)))  
SControlAv.w = '0.14'

# Synapses GControl -> GRe
SControlRe = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SControlRe.connect(i=0, j=range(len(GRe)))  
SControlRe.w = '0.036'#33ms 0.003>x>0.002

# Synapses GAv -> GRe pour inhiber
SInhib = Synapses(GAv, GRe, on_pre='v_post = 0')
SInhib.connect(condition='i==j')  

#Synapses pour aller a droite et a gauche en avancant
SVitesseAvance_cote_droit = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_droit.connect(i=0, j = odd_numbers(NB_PATTES))
SVitesseAvance_cote_droit.w = '0.05'

SVitesseAvance = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance.connect(i=1, j = range(len(GAv)))
SVitesseAvance.w = '0.05'

SVitesseRecul = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul.connect(i=2, j = range(len(GRe)))
SVitesseRecul.w = '0.018'


SVitesseAvance_cote_gauche = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_gauche.connect(i=1, j = even_numbers(NB_PATTES))
SVitesseAvance_cote_gauche.w = '0.05'

#Synapses pour aller a droite et a gauche en reculant
SVitesseRecul_cote_droit = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_droit.connect(i=0, j = odd_numbers(NB_PATTES))
SVitesseRecul_cote_droit.w = '0.018'

SVitesseRecul_cote_gauche = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_gauche.connect(i=1, j = even_numbers(NB_PATTES))
SVitesseRecul_cote_gauche.w = '0.018'

# OBSTACLES
# DEVANT
#SI il y a un obstacle devant : GControl passe de  "avance " à "recule"  
SObstacleDevantControl = Synapses(GObstacleDevant, GControl, 'w : 1', on_pre='v_post -= w')
SObstacleDevantControl.connect(i=0, j=0)  
SObstacleDevantControl.w = '0.235'

# SI il y a un obstacle devant : on stop les actions de tourner 
# SObstacleDevant_GVitesseAvance = Synapses(GObstacleDevant, GVitesseAvance, 'w : 1', on_pre='v_post = w')
# SObstacleDevant_GVitesseAvance.connect(i=0, j=range(len(GVitesseAvance)))  
# SObstacleDevant_GVitesseAvance.w = '0'

# A DROITE
SObstacledroite_GVitesseAvance = Synapses(GObstacleDroite, GVitesseAvance, 'w : 1', on_pre='v_post += w')
SObstacledroite_GVitesseAvance.connect(i=0, j=0)  
SObstacledroite_GVitesseAvance.w = '0.10' 

SObstacledroite_GVitesseRecule= Synapses(GObstacleDroite, GVitesseRecul, 'w : 1', on_pre='v_post += w')
SObstacledroite_GVitesseRecule.connect(i=1, j=0)  
SObstacledroite_GVitesseRecule.w = '0.011' 


# A GAUCHE
SObstaclegauche_GVitesseAvance = Synapses(GObstacleGauche, GVitesseAvance, 'w : 1', on_pre='v_post += w')
SObstaclegauche_GVitesseAvance.connect(i=0, j=1)  
SObstaclegauche_GVitesseAvance.w = '0.10' 

SObstaclegauche_GVitesseRecule= Synapses(GObstacleGauche, GVitesseRecul, 'w : 1', on_pre='v_post += w')
SObstaclegauche_GVitesseRecule.connect(i=1, j=1)  
SObstaclegauche_GVitesseRecule.w = '0.011' 

# delais_av, delais_re = gestionnaire_delais(SVitesseAvance.w, SControlAv.w, SControlRe.w, SVitesseAvance_cote_gauche.w, SVitesseAvance_cote_droit.w, GVitesseAvance.I, GControl.I, GVitesseRecul.I,
#                                             float(GControl.tau[0]), float(GVitesseRecul.tau[0]), float(GVitesseRecul.tau[0]), float(GAv.tau[0]), float(GRe.tau[0]))
#         SControlAv.delay = delais_av * ms
#         SVitesseAvance.delay = delais_av * ms

#         SControlRe.delay = delais_re * ms
#         SVitesseRecul.delay = delais_re * ms

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

########################### NETWORK OPERATIONS ###########################
@network_operation(dt=0.5*ms)
def update_current():
    if GVitesseAvance.t < t_end_av- 0.5*ms and GVitesseAvance.t >= t_start_av:
        GVitesseAvance.I = [Current_Turn_Av_Left, Current_Turn_Av_Right, Current_vitesse]
        # delais_av, delais_re = gestionnaire_delais(SVitesseAvance.w, SControlAv.w, SControlRe.w, SVitesseAvance_cote_gauche.w, SVitesseAvance_cote_droit.w, GVitesseAvance.I, GControl.I, GVitesseRecul.I,
        #                                     float(GControl.tau[0]), float(GVitesseRecul.tau[0]), float(GVitesseRecul.tau[0]), float(GAv.tau[0]), float(GRe.tau[0]))
        # SControlAv.delay = delais_av * ms
        # SVitesseAvance.delay = delais_av * ms
        # SControlRe.delay = delais_re * ms
        # SVitesseRecul.delay = delais_re * ms

    if GVitesseAvance.t > t_end_av - 0.5*ms:
        GVitesseAvance.I = [Current_Turn_default, Current_Turn_default, Current_vitesse]
        # delais_av, delais_re = gestionnaire_delais(SVitesseAvance.w, SControlAv.w, SControlRe.w, SVitesseAvance_cote_gauche.w, SVitesseAvance_cote_droit.w, GVitesseAvance.I, GControl.I, GVitesseRecul.I,
        #                                     float(GControl.tau[0]), float(GVitesseRecul.tau[0]), float(GVitesseRecul.tau[0]), float(GAv.tau[0]), float(GRe.tau[0]))
        # SControlAv.delay = delais_av * ms
        # SVitesseAvance.delay = delais_av * ms

        # SControlRe.delay = delais_re * ms
        # SVitesseRecul.delay = delais_re * ms
    if GVitesseRecul.t < t_end_re- 0.5*ms and GVitesseRecul.t >= t_start_re:
        GVitesseRecul.I = [Current_Turn_Re_Left, Current_Turn_Re_Right, Current_vitesse]
    if GVitesseRecul.t > t_end_re -0.5*ms:
        GVitesseRecul.I = [Current_Turn_default, Current_Turn_default, Current_vitesse]


@network_operation(dt=0.2*ms)
def update_obstacle_devant():
    if GObstacleDevant.t >= t_start_obstacle_devant and GObstacleDevant.t < t_end_obstacle_devant:
        GObstacleDevant.I = CURRENT_OBSTACLE 
    if GObstacleDevant.t >= t_end_obstacle_devant:
        GObstacleDevant.I = CURRENT_NO_OBSTACLE 

@network_operation(dt=0.5*ms)
def update_obstacle_droite():
    if ACTION == 2:
        if GObstacleDroite.t >= t_start_obstacle_droite and GObstacleDroite.t < t_end_obstacle_droite:
            GObstacleDroite.I = [CURRENT_OBSTACLE , CURRENT_NO_OBSTACLE]
        if GObstacleDroite.t >= t_end_obstacle_droite:
                GObstacleDroite.I = [CURRENT_NO_OBSTACLE ,CURRENT_NO_OBSTACLE]

    if ACTION == 1:
        if GObstacleDroite.t >= t_start_obstacle_droite and GObstacleDroite.t < t_end_obstacle_droite:
            GObstacleDroite.I = [CURRENT_NO_OBSTACLE,CURRENT_OBSTACLE ]
        if GObstacleDroite.t >= t_end_obstacle_droite:
            GObstacleDroite.I = [CURRENT_NO_OBSTACLE ,CURRENT_NO_OBSTACLE]


@network_operation(dt=1*ms)
def update_obstacle_gauche():
    if ACTION == 2:
        if GObstacleGauche.t >= t_start_obstacle_gauche and GObstacleGauche.t < t_end_obstacle_gauche:
            GObstacleGauche.I = [CURRENT_OBSTACLE , CURRENT_NO_OBSTACLE]
        if GObstacleGauche.t >= t_end_obstacle_gauche:
            GObstacleGauche.I = [CURRENT_NO_OBSTACLE ,CURRENT_NO_OBSTACLE]

    if ACTION == 1:
        if GObstacleGauche.t >= t_start_obstacle_gauche and GObstacleGauche.t < t_end_obstacle_gauche:
            GObstacleGauche.I = [CURRENT_NO_OBSTACLE,CURRENT_OBSTACLE ]
        if GObstacleGauche.t >= t_end_obstacle_gauche:
            GObstacleGauche.I = [CURRENT_NO_OBSTACLE ,CURRENT_NO_OBSTACLE]


run(300*ms)




############################## AFTER RUN ################################################
# Control direction

spike_times_ctrl = spike_monitor_ctrl.spike_trains()[0]
delays_between_spikes_ctrl = diff(spike_times_ctrl)



#reculer
spike_times_neuron_0_re = spike_monitor_re.spike_trains()[0]
spike_times_neuron_1_re = spike_monitor_re.spike_trains()[1]
delays_between_spikes_0_re = diff(spike_times_neuron_0_re)
delays_between_spikes_1_re = diff(spike_times_neuron_1_re)

# avancer
spike_times_neuron_0_av = spike_monitor_av.spike_trains()[0]
spike_times_neuron_1_av = spike_monitor_av.spike_trains()[1]
delays_between_spikes_0_av = diff(spike_times_neuron_0_av)
delays_between_spikes_1_av = diff(spike_times_neuron_1_av)

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
#print(f"Délais entre les spikes pour le CONTROL : {delays_between_spikes_ctrl}")

# Afficher les résultats
print(f"\n-------------------------------- OBSTACLE DEVANT -------------------------------------------------------")

#print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0_re}")
#print(f"Délais entre les spikes pour le OBSTACLE DEVANT : {delays_between_spikes_obst_devant}")


print(f"\n-------------------------------- RECULER -------------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0_re}")
print(f"Délais entre les spikes pour le neurone 0 : {delays_between_spikes_0_re}")
print(f"Temps de spikes pour le neurone 1 : {spike_times_neuron_1_re}")
print(f"Délais entre les spikes pour le neurone 1 : {delays_between_spikes_1_re}")
print(f"\n--------------------------------  AVANCER ------------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 (Avancer) : {spike_times_neuron_0_av}")
print(f"Délais entre les spikes pour le neurone 0 (Avancer) : {delays_between_spikes_0_av}")
print(f"Temps de spikes pour le neurone 1 (Avancer) : {spike_times_neuron_1_av}")
print(f"Délais entre les spikes pour le neurone 1 (Avancer) : {delays_between_spikes_1_av}")


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
fig1, axes = plt.subplots(4, 1, sharex=True)
fig1.suptitle(f'{Text} en allant {TextDirection}, obstacle ({TexteObstacle}  de {OBSTACLE[1]} a {OBSTACLE[2]}', fontsize=16)
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

ax = axes[0]
ax.plot(MAv.t/ms, MAv.v[0], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone 0 Avancer ( PATTES DE GAUCHE)')

ax = axes[1]
ax.plot(MRe.t/ms, MRe.v[0], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 Reculer ( PATTES DE GAUCHE)')

ax = axes[2]
ax.plot(MVitesseAvance.t/ms, MVitesseAvance.v[1], color='blue')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 1 du controle de vitesse en avancant')

ax = axes[3]
ax.plot(MVitesseRecul.t/ms, MVitesseRecul.v[1], color='grey')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 1 du controle de vitesse en reculant')



fig1.tight_layout(rect=[0.01, 0.01, 0.01, 0.01])  # Ajuste les limites de la figure
fig1.subplots_adjust(hspace=0.7)  # Ajuste l'espacement vertical entre les sous-graphes

fig2, axes = plt.subplots(4, 1, sharex=True)
fig2.suptitle(f'{Text} en allant {TextDirection}, obstacle ({TexteObstacle}  de {OBSTACLE[1]} a {OBSTACLE[2]}', fontsize=16)

# ax = axes[0]
# ax.plot(MControl.t/ms, MControl.v[0], color='blue')
# ax.axhline(y=seuilControle, ls='--', color='g')
# ax.set_ylabel('Potentiel')
# ax.set_title(f'Neurone controle de direction avec courant pour {Text} ')

ax = axes[0]
ax.plot(MAv.t/ms, MAv.v[1], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone 1 Avancer ( PATTES DE DROITE)')

ax = axes[1]
ax.plot(MRe.t/ms, MRe.v[1], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 1 Reculer ( PATTES DE DROITE)')

ax = axes[2]
ax.plot(MVitesseAvance.t/ms, MVitesseAvance.v[0], color='blue')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 du controle de vitesse en avancant')

ax = axes[3]
ax.plot(MVitesseRecul.t/ms, MVitesseRecul.v[0], color='grey')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 du controle de vitesse en reculant')



fig2.tight_layout(rect=[0.01, 0.01, 0.01, 0.01])  # Ajuste les limites de la figure
fig2.subplots_adjust(hspace=0.7)  # Ajuste l'espacement vertical entre les sous-graphes


# VERIFIER LE BON DEPHASE DES PATTES POUR LE GROUPE AVANCER                 NE PAS SUPPRIMER

fig3, axes = plt.subplots(NB_PATTES, 1, sharex=True)
for i in range(NB_PATTES):
    ax = axes[i]
    ax.plot(MAv.t/ms, MAv.v[i], color='orange')
    ax.axhline(y=seuilAv, ls='--', color='g')
    ax.axhline(y=seuilAv/2, ls='--', color='r')
    ax.set_ylabel('Potentiel')
    ax.set_title(f'Neurone {i} Avancer')

########### OU

# fig3, axes = plt.subplots(2, 1, sharex=True)
# fig3.suptitle('Groupe de Neurones Avancer', fontsize=16)
# ax_pairs = axes[0]  
# ax_odds = axes[1]   
# colors_spectre = plt.cm.viridis(np.linspace(0, 1, NB_PATTES))
# labels_pairs = []
# labels_odds = []

# for i in range(NB_PATTES):
#     if i % 2 == 0:  
#         ax_pairs.plot(MAv.t/ms, MAv.v[i], color=colors_spectre[i], label=f'Neurone {i} Avancer')
# ax_pairs.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
# ax_pairs.legend(loc='upper right')


# for i in range(NB_PATTES):
#     if i % 2 != 0:  
#         ax_odds.plot(MAv.t/ms, MAv.v[i], color=colors_spectre[i], label=f'Neurone {i} Avancer')
# ax_odds.axhline(y=seuilAv, ls='--', color='r', label=f'Seuil')
# ax_odds.legend(loc='upper right')

# ax_pairs.set_ylabel('Potentiel (neurones pairs)')
# ax_pairs.set_title('Neurones pairs')
# ax_odds.set_ylabel('Potentiel (neurones impairs)')
# ax_odds.set_title('Neurones impairs')
# axes[-1].set_xlabel('Temps (ms)')



##### VERIFIER LE BON DEPHASE DES PATTES POUR LE GROUPE RECULER  ####            NE PAS SUPPRIMER

# fig4, axes = plt.subplots(NB_PATTES, 1, sharex=True)
# for i in range(NB_PATTES):
#     ax = axes[i]
#     ax.plot(MRe.t/ms, MRe.v[i], color='red')
#     ax.axhline(y=seuilRe, ls='--', color='g')
#     ax.set_ylabel('Potentiel')
#     ax.set_title(f'Neurone {i} Reculer')

# fig4.tight_layout()

########################## OU


# fig4, axes = plt.subplots(2, 1, sharex=True)
# fig4.suptitle('Groupe de Neurones Reculer', fontsize=16)
# ax_pairs = axes[0]  
# ax_odds = axes[1]   
# colors_spectre = plt.cm.viridis(np.linspace(0, 1, NB_PATTES))
# labels_pairs = []
# labels_odds = []

# for i in range(NB_PATTES):
#     if i % 2 == 0:  
#         ax_pairs.plot(MRe.t/ms, MRe.v[i], color=colors_spectre[i], label=f'Neurone {i} Reculer')
# ax_pairs.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
# ax_pairs.legend(loc='upper right')


# for i in range(NB_PATTES):
#     if i % 2 != 0:  
#         ax_odds.plot(MRe.t/ms, MRe.v[i], color=colors_spectre[i], label=f'Neurone {i} Reculer')
# ax_odds.axhline(y=seuilRe, ls='--', color='r', label=f'Seuil')
# ax_odds.legend(loc='upper right')

# ax_pairs.set_ylabel('Potentiel (neurones pairs)')
# ax_pairs.set_title('Neurones pairs')
# ax_odds.set_ylabel('Potentiel (neurones impairs)')
# ax_odds.set_title('Neurones impairs')
# axes[-1].set_xlabel('Temps (ms)')


# Paramètres simples pour un modèle de neurone
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
