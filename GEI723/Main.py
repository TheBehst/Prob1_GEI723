from brian2 import *
import matplotlib.pyplot as plt
import math

############################### 3 CHOIX UTILISATEURS ################################################

TURN =1# 0 = STRAIGHT, 1 = LEFT, 2 = RIGHT
ACTION = 1#2 = AVANCER, 1 = RECULER
NB_PATTES = 6 # doit etre pair
VITESSE = 1 #
#NB: L'action de tourner commence des que la variable TURN est changée

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
TextDirection = "a gauche" if TURN == 1 else "a droite" if TURN == 2 else "tout droit"

#################################### DEF ##########################################
def estimate_spike_frequency(I, tau, threshold, reset_value, v_init=0):

    if I <= threshold:
        # If input current is not enough to reach the threshold, the neuron won't spike
        return 0
    
    # Calculate the time it takes to reach the threshold
    time_to_spike = -tau * math.log((threshold - I) / (v_init - I))
    
    # Total period of spiking includes the time to reset as well
    time_to_reset = -tau * math.log((reset_value - I) / (v_init - I))
    
    # Calculate the total time for one spike cycle (spike + reset)
    total_spike_cycle_time = time_to_spike + time_to_reset
    
    
    return total_spike_cycle_time


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
    
    if ACTION == 2 and TURN != 0:  # Avancer
        t_start_av = t_start_base_av + dephase
        t_end_av = t_end_base_av + dephase
        t_start_re = 0* ms 
        t_end_re = 0* ms 
    elif ACTION == 1 and TURN != 0:  # Reculer
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


# pour tourner

# TODO Modifier ces temps dans le cas ou y a le dephase : je GVitesse doit se stoper avant ( du temps de dephasage)
# POUR eviter le 24.2  dans : par exemple

# tourner a droite :
#neurone 0 (Avancer) : [3.  3.  3.  3.  3.  3.  3.  3.  3.  3.  3.  4.8 6.  6.  6.

# tourner a gauche :
#neurone 1 (Avancer) : [3.  3.  3.  3.  3.  3.  3.  3.  3.  3.  4.2 6.  6.  6.





start_scope()

SeuilTourner = 0.1
seuilAv = 1
seuilRe = 0.5
seuilControle = 0.9

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
GAv = NeuronGroup(NB_PATTES, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GRe = NeuronGroup(NB_PATTES, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')

GVitesseAvance = NeuronGroup(3, eqs, threshold='v>=SeuilTourner', reset='v=0', method='euler')# neurones pour controler les 2 cotes des pattes séparément

GVitesseRecul = NeuronGroup(3, eqs, threshold='v>=SeuilTourner', reset='v=0', method='euler')

GControl.tau = 1 * ms#pour que le controle spike a interval tres court avec I=1 et I=2
GAv.tau = 10 * ms 
GRe.tau = 500 * ms
GControl.I = Current

GVitesseAvance.I = [Current_Turn_default, Current_Turn_default]
GVitesseAvance.tau = 10 * ms

GVitesseRecul.I = [Current_Turn_default, Current_Turn_default]
GVitesseRecul.tau = 50* ms#


@network_operation(dt=0.5*ms)  # Met à jour à chaque pas de temps
def update_current():
    if GVitesseAvance.t < t_end_av- 0.5*ms and GVitesseAvance.t >= t_start_av:
        GVitesseAvance.I = [Current_Turn_Av_Left, Current_Turn_Av_Right]
    if GVitesseAvance.t > t_end_av - 0.5*ms:
        GVitesseAvance.I = [Current_Turn_default, Current_Turn_default]

    if GVitesseRecul.t < t_end_re- 0.5*ms and GVitesseRecul.t >= t_start_re:
        GVitesseRecul.I = [Current_Turn_Re_Left, Current_Turn_Re_Right]
    if GVitesseRecul.t > t_end_re -0.5*ms:
        GVitesseRecul.I = [Current_Turn_default, Current_Turn_default]

################################ SYNAPSES ###############################################


SControlAv = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w')
SControlAv.connect(i=0, j=range(len(GAv)))  
SControlAv.w = '0.14'#6ms
SControlAv.delay = delay_maker(NB_PATTES,0,3)* ms

# Synapses GControl -> GRe
SControlRe = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SControlRe.connect(i=0, j=range(len(GRe)))  
SControlRe.w = '0.036'#33ms
SControlRe.delay = delay_maker(NB_PATTES,0, 16.5) * ms

# Synapses GAv -> GRe pour inhiber
SInhib = Synapses(GAv, GRe, on_pre='v_post = 0')
SInhib.connect(condition='i==j')  


SVitesseAvance = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance.connect(i=2, j = range(len(GAv)))
SVitesseAvance.w = '0.05'

SVitesseRecule = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecule.connect(i=2, j = range(len(GRe)))
SVitesseRecule.w = '0.018'

#Synapses pour aller a droite et a gauche en avancant
SVitesseAvance_cote_droit = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_droit.connect(i=0, j = odd_numbers(NB_PATTES))
SVitesseAvance_cote_droit.w = '0.05'


SVitesseAvance_cote_gauche = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_gauche.connect(i=1, j = even_numbers(NB_PATTES))
SVitesseAvance_cote_gauche.w = '0.05'

#Synapses pour aller a droite et a gauche en reculant
SVitesseRecul_cote_droit = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_droit.connect(i=0, j = odd_numbers(NB_PATTES))
#SVitesseRecul_cote_droit.connect(i=2, j = range(NB_PATTES))
SVitesseRecul_cote_droit.w = '0.018'

SVitesseRecul_cote_gauche = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_gauche.connect(i=1, j = even_numbers(NB_PATTES))
SVitesseRecul_cote_gauche.w = '0.018'



MControl = StateMonitor(GControl, 'v', record=True)
MAv = StateMonitor(GAv, 'v', record=True)
MRe = StateMonitor(GRe, 'v', record=True)
MVitesseAvance = StateMonitor(GVitesseAvance, 'v', record=True)
MVitesseRecul = StateMonitor(GVitesseRecul, 'v', record=True)


# Moniteur pour enregistrer les spikes des neurones
spike_monitor_re = SpikeMonitor(GRe)
spike_monitor_av = SpikeMonitor(GAv)
spike_monitor_CtrlVit_AV = SpikeMonitor(GVitesseAvance)
spike_monitor_CtrlVit_Re = SpikeMonitor(GVitesseRecul)


run(300*ms)#pour reculer, pour avancer on peut sur 500 c est suffisant




############################## AFTER RUN ################################################

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

# Afficher les résultats
print(f"-------------------------------- RECULER -------------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0_re}")
print(f"Délais entre les spikes pour le neurone 0 : {delays_between_spikes_0_re}")
print(f"Temps de spikes pour le neurone 1 : {spike_times_neuron_1_re}")
print(f"Délais entre les spikes pour le neurone 1 : {delays_between_spikes_1_re}")
print(f"---------------------------------  AVANCER ------------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 (Avancer) : {spike_times_neuron_0_av}")
print(f"Délais entre les spikes pour le neurone 0 (Avancer) : {delays_between_spikes_0_av}")
print(f"Temps de spikes pour le neurone 1 (Avancer) : {spike_times_neuron_1_av}")
print(f"Délais entre les spikes pour le neurone 1 (Avancer) : {delays_between_spikes_1_av}")


# print(f"---------------------------------- CTRLVIT_AV -----------------------------------------------------")

# print(f"Temps de spikes pour le neurone 0 (CtrlVit_AV) : {spike_times_neuron_0_CtrlVit_AV}")
# print(f"Délais entre les spikes pour le neurone 0 (CtrlVit_AV) : {delays_between_spikes_0_CtrlVit_AV}")
# print(f"Temps de spikes pour le neurone 1 (CtrlVit_AV) : {spike_times_neuron_1_CtrlVit_AV}")
# print(f"Délais entre les spikes pour le neurone 1 (CtrlVit_AV) : {delays_between_spikes_1_CtrlVit_AV}")

# print(f"---------------------------------- CTRLVIT_Re -----------------------------------------------------")

# print(f"Temps de spikes pour le neurone 0 (CtrlVit_Re) : {spike_times_neuron_0_CtrlVit_Re}")
# print(f"Délais entre les spikes pour le neurone 0 (CtrlVit_Re) : {delays_between_spikes_0_CtrlVit_Re}")
# print(f"Temps de spikes pour le neurone 1 (CtrlVit_Re) : {spike_times_neuron_1_CtrlVit_Re}")
# print(f"Délais entre les spikes pour le neurone 1 (CtrlVit_Re) : {delays_between_spikes_1_CtrlVit_Re}")
##############################################################################

# Visualiser les résultats
fig1, axes = plt.subplots(4, 1, sharex=True)
fig1.suptitle(f'{Text} en allant {TextDirection}', fontsize=16)
# ax = axes[0]
# ax.plot(MControl.t/ms, MControl.v[0], color='blue')
# ax.axhline(y=seuilControle, ls='--', color='g')
# ax.set_ylabel('Potentiel')
# ax.set_title(f'Neurone de controle de direction  avec courant pour {Text} ')

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
ax.set_title('Neurone 1 du controle de vitesse en avancant :tourner a droite, accelerer gauche')

ax = axes[3]
ax.plot(MVitesseRecul.t/ms, MVitesseRecul.v[1], color='grey')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 1 du controle de vitesse en reculant :tourner a droite, accelerer gauche')



fig1.tight_layout(rect=[0.01, 0.01, 0.01, 0.01])  # Ajuste les limites de la figure
fig1.subplots_adjust(hspace=0.7)  # Ajuste l'espacement vertical entre les sous-graphes

fig2, axes = plt.subplots(4, 1, sharex=True)
fig2.suptitle(f'{Text} en allant {TextDirection}', fontsize=16)

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
ax.set_title('Neurone 0 du controle de vitesse en avancant:  tourner a gauche, accelerer droit')

ax = axes[3]
ax.plot(MVitesseRecul.t/ms, MVitesseRecul.v[0], color='grey')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 du controle de vitesse en reculant:  tourner a gauche, accelerer droit')



fig2.tight_layout(rect=[0.01, 0.01, 0.01, 0.01])  # Ajuste les limites de la figure
fig2.subplots_adjust(hspace=0.7)  # Ajuste l'espacement vertical entre les sous-graphes


# VERIFIER LE BON DEPHASE DES PATTES POUR LE GROUPE AVANCER                 NE PAS SUPPRIMER

fig3, axes = plt.subplots(NB_PATTES, 1, sharex=True)
for i in range(NB_PATTES):
    ax = axes[i]
    ax.plot(MAv.t/ms, MAv.v[i], color='orange')
    ax.axhline(y=seuilAv, ls='--', color='g')
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
