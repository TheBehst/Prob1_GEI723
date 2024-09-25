from brian2 import *
import matplotlib.pyplot as plt
import math
# 0 = STRAIGHT, 1 = LEFT, 2 = RIGHT
TURN = 1
#1 = AVANCER, 2 = RECULER
ACTION = 1
LARGE_CURRENT = 2
SMALL_CURRENT = 1

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
    return [i for i in range(0, N+1, 2)]
start_scope()
seuilAv = 1
seuilRe = 0.9
seuilControle = 0.9
eqs = """
dv/dt = (I-v) / tau : 1
tau : second
I : 1
"""
GControl = NeuronGroup(5, eqs, threshold='v>seuilControle', reset='v=0', method='euler')
GAv = NeuronGroup(6, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GRe = NeuronGroup(6, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GVitesseRecul = NeuronGroup(2, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GVitesseAvance = NeuronGroup(2, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GControl.tau = 10 * ms
GAv.tau = 10 * ms
GRe.tau = 1000 * ms
GControl.I = [SMALL_CURRENT, ]



SControlAv = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w')
SControlAv.connect(i=0, j=range(len(GAv)))  
SControlAv.w = '0.5'
SControlAv.delay = delay_maker(6,0,15)* ms

# Synapses GControl -> GRe
SControlRe = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SControlRe.connect(i=0, j=range(len(GRe)))  
SControlRe.w = '0.1'
SControlRe.delay = delay_maker(6,10, 115) * ms

# Synapses GAv -> GRe pour inhiber
SInhib = Synapses(GAv, GRe, on_pre='v_post = 0')
SInhib.connect(condition='i==j')  

SVitesseRecul_cote_droite = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_droite.connect(i=1, j = odd_numbers(6))

SVitesseRecul_cote_gauche = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SVitesseRecul_cote_gauche.connect(i=2, j = even_numbers(6))

SVitesseAvance_cote_droite = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_droite.connect(i=3, j = odd_numbers(6))

SVitesseAvance_cote_gauche = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w')
SVitesseAvance_cote_gauche.connect(i=4, j = even_numbers(6))

SVitesseAvance = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
MControl = StateMonitor(GControl, 'v', record=True)
MAv = StateMonitor(GAv, 'v', record=True)
MRe = StateMonitor(GRe, 'v', record=True)

# Moniteur pour enregistrer les spikes des neurones
spike_monitor = SpikeMonitor(GRe)
spike_monitor_av = SpikeMonitor(GAv)
# Simulation and plot setup
run(500*ms)
spike_times_neuron_0 = spike_monitor.spike_trains()[0]
spike_times_neuron_1 = spike_monitor.spike_trains()[1]

# Calculer les délais entre les spikes pour les deux neurones
delays_between_spikes_0 = diff(spike_times_neuron_0)
delays_between_spikes_1 = diff(spike_times_neuron_1)
# Récupérer les temps de spikes pour les neurones 0 et 1 du groupe GAv (neurones qui avancent)
spike_times_neuron_0_av = spike_monitor_av.spike_trains()[0]
spike_times_neuron_1_av = spike_monitor_av.spike_trains()[1]

# Calculer les délais entre les spikes pour les neurones 0 et 1 dans GAv
delays_between_spikes_0_av = diff(spike_times_neuron_0_av)
delays_between_spikes_1_av = diff(spike_times_neuron_1_av)


# Afficher les résultats
print(f"Temps de spikes pour le neurone 0 : {spike_times_neuron_0}")
print(f"Délais entre les spikes pour le neurone 0 : {delays_between_spikes_0}")
print(f"Temps de spikes pour le neurone 1 : {spike_times_neuron_1}")
print(f"Délais entre les spikes pour le neurone 1 : {delays_between_spikes_1}")
print(f"---------------------------------------------------------------------------------------")

print(f"Temps de spikes pour le neurone 0 (Avancer) : {spike_times_neuron_0_av}")
print(f"Délais entre les spikes pour le neurone 0 (Avancer) : {delays_between_spikes_0_av}")
print(f"Temps de spikes pour le neurone 1 (Avancer) : {spike_times_neuron_1_av}")
print(f"Délais entre les spikes pour le neurone 1 (Avancer) : {delays_between_spikes_1_av}")
# Visualiser les résultats
fig1, axes = plt.subplots(3, 1, sharex=True)
ax = axes[0]
ax.plot(MControl.t/ms, MControl.v[0], color='blue')
ax.axhline(y=seuilControle, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title(f'Neurone controle avec courant pour {ACTION}')
ax = axes[1]
ax.plot(MAv.t/ms, MAv.v[0], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone 0 Avancer')
ax = axes[2]
ax.plot(MRe.t/ms, MRe.v[0], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone 0 Reculer')
fig1.tight_layout()

fig2, axes = plt.subplots(6, 1, sharex=True)
for i in range(6):
    ax = axes[i]
    ax.plot(MAv.t/ms, MAv.v[i], color='orange')
    ax.axhline(y=seuilAv, ls='--', color='g')
    ax.set_ylabel('Potentiel')
    ax.set_title(f'Neurone {i} Avancer')
fig3, axes = plt.subplots(6, 1, sharex=True)
for i in range(6):
    ax = axes[i]
    ax.plot(MRe.t/ms, MRe.v[i], color='red')
    ax.axhline(y=seuilRe, ls='--', color='g')
    ax.set_ylabel('Potentiel')
    ax.set_title(f'Neurone {i} Reculer')

fig1.tight_layout()
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
visualise_connectivity(SInhib)
plt.show()
