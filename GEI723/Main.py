from brian2 import *
import matplotlib.pyplot as plt

# Paramètres simples pour un modèle de neurone
start_scope()
seuilAv = 20
seuilRe = 15
current = 10
eqs = """
dv/dt = (I-v) / tau : 1
tau : second
I : 1
"""
GControl = NeuronGroup(1, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GAv = NeuronGroup(6, eqs, threshold='v>=seuilAv', reset='v=0', method='euler')
GRe = NeuronGroup(6, eqs, threshold='v>=seuilRe', reset='v=0', method='euler')
GControl.tau = 10 * ms
# Courant en entrée
GControl.I = current
# Définition des synapses
SControl = Synapses(GControl, GAv, 'w : 1', on_pre='v_post += w')
# Connexion des synapses
SControl.connect(i=0, j=[0, 3, 4])
# Poids des synapses
SControl.w = 'j*0.2'
# Délai de propagation
SControl.delay = [0.5*ms, 0.8*ms]
print(GControl.tau)





# Durée de simulation
duration = 100*ms
# Moniteur du potentiel membranaire
statemon = StateMonitor(GAv, 'v', record=True)

# Lancer la simulation
run(duration)

# Visualiser les résultats
fig, ax = plt.subplots(1, 1)
ax.plot(statemon.t/ms, statemon.v[0], label='Potentiel membranaire')
ax.axhline(y=theta, color='r', linestyle='--', label='Seuil de décharge')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('u(t)')
ax.legend()
plt.show()

