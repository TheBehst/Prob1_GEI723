from brian2 import *
import matplotlib.pyplot as plt

MODE = "RECULER"
LARGE_CURRENT = 2
SMALL_CURRENT = 1


start_scope()
seuilAv = 1
seuilRe = 0.9
seuilControle = 0.9
eqs = """
dv/dt = (I-v) / tau : 1
tau : second
I : 1
"""
GControl = NeuronGroup(1, eqs, threshold='v>seuilControle', reset='v=0', method='euler')
GAv = NeuronGroup(6, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GRe = NeuronGroup(6, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GControl.tau = 10 * ms
GAv.tau = 10 * ms
GRe.tau = 1000 * ms
if MODE == "AVANCER":
    GControl.I = LARGE_CURRENT
    GAv.I = LARGE_CURRENT
else: 
    GControl.I = SMALL_CURRENT
    GAv.I = SMALL_CURRENT
GRe.I = 0
GAv.v = [0, seuilAv/2, seuilAv/2, 0, 0, seuilAv/2]
GRe.v = [0, seuilRe/2, seuilRe/2, 0, 0, seuilRe/2]


# Synapses GControl -> GRe
SControlRe = Synapses(GControl, GRe, 'w : 1', on_pre='v_post += w')
SControlRe.connect(i=0, j=range(len(GRe)))  # Connect to all neurons in GRe
SControlRe.w = '0.4'
SControlRe.delay = np.array([0.10, 0.20] * 3) * ms

# Synapses GAv -> GRe pour inhiber
SInhib = Synapses(GAv, GRe, on_pre='v_post = 0')
SInhib.connect(condition='i==j')  


MControl = StateMonitor(GControl, 'v', record=True)
MAv = StateMonitor(GAv, 'v', record=True)
MRe = StateMonitor(GRe, 'v', record=True)
# Simulation and plot setup (if required)
run(500*ms)

# Visualiser les résultats
fig1, axes = plt.subplots(3, 1, sharex=True)
ax = axes[0]
ax.plot(MControl.t/ms, MControl.v[0], color='blue')
ax.axhline(y=seuilControle, ls='--', color='g')
ax.set_ylabel('Potentiel')
ax.set_title(f'Neurone controle avec courant pour {MODE}')
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
    ax.axhline(y=seuilAv, ls='--', color='g')
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
