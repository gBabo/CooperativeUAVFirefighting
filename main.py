from simulation import Simulation

sim = Simulation()

while sim.running:
    # sim.main_menu.display_menu()
    sim.initiate()
    sim.simulation_loop()
