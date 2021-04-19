from simulation import Simulation


if __name__ == "__main__":
    sim = Simulation()

    while sim.running:
        sim.initiate()
        sim.simulation_loop()
