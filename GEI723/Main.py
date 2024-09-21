from brian2 import *
import matplotlib.pyplot as plt

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


start_scope()
# valeurs initiales a re calculer 
seuilAv = 50
seuilRe = 40
seuilControle = 1
current = 16
#10A, 16A
eqs = """
dv/dt = (I-v)/ tau : 1
tau : second
I : 1
"""
GControl = NeuronGroup(1, eqs, threshold='v>seuilControle', reset='v=0', method='euler')
GAv = NeuronGroup(6, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GRe = NeuronGroup(6, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GControl.tau = 10 * ms
GAv.tau = 10 * ms
GRe.tau = 10* ms
# Courant en entrée
GControl.I = current 
GAv.I = 0
GRe.I = 0
# Définition des synapses
# Synapses GControl -> GAv
SControlAv = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w')#action du poids a redefinir
SControlAv.connect(i=0, j=range(len(GAv)))  # Connect to all neurons in GAv
SControlAv.w = '5'
SControlAv.delay = [0*ms, 1*ms, 0*ms, 1*ms, 0*ms, 1*ms]


# Synapses GControl -> GRe
SControlRe = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')#action du poids a redefinir
SControlRe.connect(i=0, j=range(len(GRe)))  # Connect to all neurons in GRe
SControlRe.w = '5'
SControlRe.delay = [10*ms, 11*ms, 10*ms, 11*ms, 10*ms, 11*ms]


#Synapses GAv -> GRe
# Synapse GAv -> GRe pour inhibition
SInhibAvRe = Synapses(GAv, GRe, on_pre='v_post = -100')  # Inhibition totale des neurones Re
SInhibAvRe.connect(i=0, j=range(len(GRe)))  # Connecter tous les neurones de Av à tous les neurones de Re
SInhibAvRe.delay = 0*ms  


MControl = StateMonitor(GControl, 'v', record=True)
MAv = StateMonitor(GAv, 'v', record=True)
MRe = StateMonitor(GRe, 'v', record=True)
# Simulation and plot setup (if required)
# Spike monitors pour vérifier les spikes
# spike_mon_GAv = SpikeMonitor(GAv)
# spike_mon_GRe = SpikeMonitor(GRe)
run(100*ms)

# Visualiser les résultats
fig, axes = plt.subplots(3, 1, sharex=True)
ax = axes[0]
ax.plot(MControl.t/ms, MControl.v[0], color='blue')
ax.axhline(y=seuilControle, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title(f'Neurone controle avec courant {current}')
ax = axes[1]
ax.plot(MAv.t/ms, MAv.v[0], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone Avancer 0')

ax = axes[2]
ax.plot(MAv.t/ms, MAv.v[1], color='orange')
ax.axhline(y=seuilAv, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title('Neurone Avancer 1')


#visualise_connectivity(SInhib)


fig, axes = plt.subplots(3, 1, sharex=True)
ax = axes[0]
ax.plot(MControl.t/ms, MControl.v[0], color='blue')
ax.axhline(y=seuilControle, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title(f'Neurone controle avec courant {current}')


ax = axes[1]
ax.plot(MRe.t/ms, MRe.v[0], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone Reculer 0')

ax = axes[2]
ax.plot(MRe.t/ms, MRe.v[1], color='red')
ax.axhline(y=seuilRe, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_xlabel('Temps (ms)')
ax.set_title('Neurone Reculer 1')
fig.tight_layout()
#visualise_connectivity(SInhib)
plt.show()




# print(f"Spikes dans GAv: {spike_mon_GAv.count}")
# print(f"Spikes dans GRe: {spike_mon_GRe.count}")