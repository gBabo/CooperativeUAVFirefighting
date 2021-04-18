from simulation import Simulation

sim = Simulation()

while sim.running:
    sim.initiate()
    sim.simulation_loop()
