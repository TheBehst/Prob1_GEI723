from brian2 import *
import matplotlib.pyplot as plt
import math

############################### 3 CHOIX UTILISATEURS ################################################

TURN = 1 # 0 = STRAIGHT, 1 = LEFT, 2 = RIGHT
ACTION = 2 #2 = AVANCER, 1 = RECULER
NB_PATTES = 6 # doit etre pair

#NB: L'action de tourner commence des que la variable TURN est changée, et dure xxxx temps le temps de tourner 
# pour l instant, j ai mis 5 spikes 


# VERIFICATION ET VALEURS PAR DEFAUT
if not (NB_PATTES > 0 and NB_PATTES % 2 == 0):
    NB_PATTES = 6

if ACTION not in [1, 2]:
    ACTION = 1

Text = "avancer" if ACTION == 2 else "reculer"
TextDirection = "a gauche" if TURN == 1 else "a droite" if TURN == 2 else "tout droit"

#################################### DEF ##########################################



def delay_maker(N, start, delay):
    result = []
    for i in range(N):
        if i % 4 == 0 or i % 4 == 3:  
            result.append(start)
        else:  
            result.append(start + delay)
    return result

def odd_numbers(N):
    return [i for i in range(1, N+1, 2)]
def even_numbers(N):
    return [i for i in range(0, N, 2)]


############################### VALEURS INITS ################################################



LARGE_CURRENT = 2
SMALL_CURRENT = 1
CURRENT_TURN_AV = 1.285#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!essai erreur pour reduire de moite les delais entre spike, donc double vitesse d un cote pour tourner
CURRENT_TURN_RE = 1

Current = LARGE_CURRENT if ACTION == 2 else SMALL_CURRENT

Current_Turn_Av_Left = CURRENT_TURN_AV if TURN ==  1 and ACTION == 2 else 0
Current_Turn_Av_Right = CURRENT_TURN_AV if TURN ==  2  and ACTION == 2 else 0
Current_Turn_Re_Left = CURRENT_TURN_RE if TURN ==  1 and ACTION == 1 else 0
Current_Turn_Re_Right = CURRENT_TURN_RE if TURN ==  2  and ACTION == 1 else 0



start_scope()


SeuilTourner = 1
seuilAv = 1
seuilRe = 0.9
seuilControle = 0.9

eqs = """
dv/dt = (I-v) / tau : 1
tau : second
I : 1
spike_count : integer
"""
################################### GROUPES DE NEURONES ############################################

GControl = NeuronGroup(1, eqs, threshold='v>seuilControle', reset='v=0', method='euler')
GAv = NeuronGroup(NB_PATTES, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GRe = NeuronGroup(NB_PATTES, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GVitesseAvance = NeuronGroup(2, eqs, threshold='v>=SeuilTourner', reset='v=0; spike_count += 1; I *= (spike_count < 5)', method='euler')# neurones pour controler les 2 cotes des pattes séparément
GVitesseRecul = NeuronGroup(2, eqs, threshold='v>=seuilRe', reset='v=0; spike_count += 1; I *= (spike_count < 5)', method='euler')

GControl.tau = 10 * ms
GAv.tau = 10 * ms
GRe.tau = 1000 * ms
GControl.I = Current

GVitesseAvance.I = [Current_Turn_Av_Left, Current_Turn_Av_Right]
GVitesseAvance.tau = 10 * ms
GVitesseAvance.spike_count =0

GVitesseRecul.I = [Current_Turn_Re_Left, Current_Turn_Re_Right]
GVitesseRecul.tau = 49.99* ms#!!!!!!!!!!!!!!!!!!!!!!!!!! bidouille pour avoir Délais entre les spikes pour le neurone 0 (CtrlVit_Re) : [115. 115. 115. 115.] ms : MOITIE DE 230, delai normal
GVitesseRecul.spike_count =0

################################ SYNAPSES ###############################################


SControlAv = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w')
SControlAv.connect(i=0, j=range(len(GAv)))  
SControlAv.w = '0.5'
SControlAv.delay = delay_maker(NB_PATTES,0,15)* ms

# Synapses GControl -> GRe
SControlRe = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SControlRe.connect(i=0, j=range(len(GRe)))  
SControlRe.w = '0.1'
SControlRe.delay = delay_maker(NB_PATTES,10, 115) * ms

# Synapses GAv -> GRe pour inhiber
SInhib = Synapses(GAv, GRe, on_pre='v_post = 0')
SInhib.connect(condition='i==j')  

# SVitesseRecul_cote_droite = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
# SVitesseRecul_cote_droite.connect(i=1, j = odd_numbers(6))

# SVitesseRecul_cote_gauche = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
# SVitesseRecul_cote_gauche.connect(i=2, j = even_numbers(6))

# SVitesseAvance_cote_droite = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w')
# SVitesseAvance_cote_droite.connect(i=3, j = odd_numbers(6))


#Synapses pour aller a droite et a gauche en avancant
SVitesseAvance_cote_droit = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_droit.connect(i=0, j = even_numbers(NB_PATTES))
SVitesseAvance_cote_droit.w = '1'
# pb : premier delai pour avancer non regulier avec autre ?
#Délais entre les spikes pour le neurone 1 (Avancer) : [ 9. 15. 15. 15. 30. 30. 30. 30. 30. 30. 30. 30. 30. 30. 30. 30. 30. 30.] ms 30 = normal
SVitesseAvance_cote_gauche = Synapses(GVitesseAvance, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_gauche.connect(i=1, j = odd_numbers(NB_PATTES))
SVitesseAvance_cote_gauche.w = '1'

#Synapses pour aller a droite et a gauche en reculant
SVitesseRecul_cote_droit = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_droit.connect(i=0, j = even_numbers(NB_PATTES))
SVitesseRecul_cote_droit.w = '1'

SVitesseRecul_cote_gauche = Synapses(GVitesseRecul, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_gauche.connect(i=1, j = odd_numbers(NB_PATTES))
SVitesseRecul_cote_gauche.w = '1'



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


run(1500*ms)#pour reculer, pour avancer on peut sur 500 c est suffisant




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


print(f"---------------------------------- CTRLVIT_AV -----------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 (CtrlVit_AV) : {spike_times_neuron_0_CtrlVit_AV}")
print(f"Délais entre les spikes pour le neurone 0 (CtrlVit_AV) : {delays_between_spikes_0_CtrlVit_AV}")
print(f"Temps de spikes pour le neurone 1 (CtrlVit_AV) : {spike_times_neuron_1_CtrlVit_AV}")
print(f"Délais entre les spikes pour le neurone 1 (CtrlVit_AV) : {delays_between_spikes_1_CtrlVit_AV}")

print(f"---------------------------------- CTRLVIT_Re -----------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 (CtrlVit_Re) : {spike_times_neuron_0_CtrlVit_Re}")
print(f"Délais entre les spikes pour le neurone 0 (CtrlVit_Re) : {delays_between_spikes_0_CtrlVit_Re}")
print(f"Temps de spikes pour le neurone 1 (CtrlVit_Re) : {spike_times_neuron_1_CtrlVit_Re}")
print(f"Délais entre les spikes pour le neurone 1 (CtrlVit_Re) : {delays_between_spikes_1_CtrlVit_Re}")
##############################################################################

# Visualiser les résultats
fig1, axes = plt.subplots(5, 1, sharex=True)
fig1.suptitle(f'{Text} en allant {TextDirection}', fontsize=16)
ax = axes[0]
ax.plot(MControl.t/ms, MControl.v[0], color='blue')
ax.axhline(y=seuilControle, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title(f'Neurone de controle de direction  avec courant pour {Text} ')

ax = axes[1]
ax.plot(MAv.t/ms, MAv.v[0], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone 0 Avancer ( PATTES DE DROITE)')

ax = axes[2]
ax.plot(MRe.t/ms, MRe.v[0], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 Reculer ( PATTES DE DROITE)')

ax = axes[3]
ax.plot(MVitesseAvance.t/ms, MVitesseAvance.v[0], color='red')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 du controle de vitesse en avancant:  tourner a gauche, accelerer droit')

ax = axes[4]
ax.plot(MVitesseRecul.t/ms, MVitesseRecul.v[0], color='red')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 du controle de vitesse en reculant:  tourner a gauche, accelerer droit')

fig1.tight_layout()

fig2, axes = plt.subplots(5, 1, sharex=True)
fig2.suptitle(f'{Text} en allant {TextDirection}', fontsize=16)

ax = axes[0]
ax.plot(MControl.t/ms, MControl.v[0], color='blue')
ax.axhline(y=seuilControle, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title(f'Neurone controle de direction avec courant pour {Text} ')

ax = axes[1]
ax.plot(MAv.t/ms, MAv.v[1], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone 1 Avancer ( PATTES DE GAUCHE)')

ax = axes[2]
ax.plot(MRe.t/ms, MRe.v[1], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 1 Reculer ( PATTES DE GAUCHE)')

ax = axes[3]
ax.plot(MVitesseAvance.t/ms, MVitesseAvance.v[1], color='red')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 1 du controle de vitesse en avancant :tourner a droite, accelerer gauche')

ax = axes[4]
ax.plot(MVitesseRecul.t/ms, MVitesseRecul.v[1], color='red')
ax.axhline(y=SeuilTourner, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 1 du controle de vitesse en reculant :tourner a droite, accelerer gauche')



fig2.tight_layout()


fig3, axes = plt.subplots(NB_PATTES, 1, sharex=True)
for i in range(NB_PATTES):
    ax = axes[i]
    ax.plot(MAv.t/ms, MAv.v[i], color='orange')
    ax.axhline(y=seuilAv, ls='--', color='g')
    ax.set_ylabel('Potentiel')
    ax.set_title(f'Neurone {i} Avancer')

fig4, axes = plt.subplots(NB_PATTES, 1, sharex=True)
for i in range(NB_PATTES):
    ax = axes[i]
    ax.plot(MRe.t/ms, MRe.v[i], color='red')
    ax.axhline(y=seuilRe, ls='--', color='g')
    ax.set_ylabel('Potentiel')
    ax.set_title(f'Neurone {i} Reculer')

fig4.tight_layout()



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
