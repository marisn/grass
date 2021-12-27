# PSO tests
import random
import math

import matplotlib.pyplot as plt
from matplotlib.path import Path


def setupSwarm():
    print("setupSwarm")
    swarm = {
        "n": 10,
        "a": 0.01,
        "b": 0.2,
        "w": 0.8,
        "c1": 0.2,
        "c2": 0.6,
        "vmax": 1.0,
        "x": (0, 100.0),
        "y": (0, 100.0),
        "gold": (random.uniform(0, 100), random.uniform(0, 100)),
        "particles": [],
        "gbest": 999,
        "gbestx": 50,
        "gbesty": 50,
    }
    for p in range(swarm["n"]):
        swarm["particles"].append(
            {
                "px": random.uniform(*swarm["x"]),
                "py": random.uniform(*swarm["y"]),
                "vx": random.random(),
                "vy": random.random(),
                "pbest": 999.0,
            }
        )
        swarm["particles"][p]["pbestx"] = swarm["particles"][p]["px"]
        swarm["particles"][p]["pbesty"] = swarm["particles"][p]["py"]
    return swarm


def updateSwarm(swarm):
    # Daļiņa dodas tieši pretējā virzienā.
    # Šīs atjaunināšanas formulas darbojās galīgi pēc piena.
    # Jāpārbauda vēlreiz pēc raksta un, ja neko aizdomīgu nemana,
    # jāuzliek sākotnējās vērtības ar roku un pēc tam jāpārbauda manuāli.
    vxs = ""
    for i in range(swarm["n"]):
        particle = swarm["particles"][i]
        vx = (
            swarm["w"] * particle["vx"]
            + swarm["c1"] * random.random() * (particle["pbestx"] - particle["px"])
            + swarm["c2"] * random.random() * (swarm["gbestx"] - particle["px"])
        )
        vy = (
            swarm["w"] * particle["vy"]
            + swarm["c1"] * random.random() * (particle["pbesty"] - particle["py"])
            + swarm["c2"] * random.random() * (swarm["gbesty"] - particle["py"])
        )
        px = particle["px"] + particle["vx"]
        py = particle["py"] + particle["vy"]
        px = swarm["x"][0] if px < swarm["x"][0] else px
        px = swarm["x"][1] if px > swarm["x"][1] else px
        particle["px"] = px
        py = swarm["y"][0] if py < swarm["y"][0] else py
        py = swarm["y"][1] if py > swarm["y"][1] else py
        particle["py"] = py
        vx = swarm["vmax"] if vx > swarm["vmax"] else vx
        vx = -1 * swarm["vmax"] if vx < -1 * swarm["vmax"] else vx
        particle["vx"] = vx
        vy = swarm["vmax"] if vy > swarm["vmax"] else vy
        vy = -1 * swarm["vmax"] if vy < -1 * swarm["vmax"] else vy
        particle["vy"] = vy
        vxs += f"{vx:8.5f} "
    print(f"vxs: {vxs}")
    # print(
        # f'px:{swarm["particles"][0]["px"]:.{6}} py:{swarm["particles"][0]["py"]:.{6}} ' +
        # f'vx:{swarm["particles"][0]["vx"]:.{6}} vy:{swarm["particles"][0]["vy"]:.{6}} ' +
        # f'pb:{swarm["particles"][0]["pbest"]:.{4}}'
    # )


def calculateParticle(particle):
    pass


def evaluateParticle(particle, swarm):
    score = math.sqrt((swarm["gold"][0] - particle["px"]) ** 2 + (swarm["gold"][1] - particle["py"]) ** 2)
    return score


def runOptimisation(swarm):
    for i in range(swarm["n"]):
        particle = swarm["particles"][i]
        calculateParticle(i)
        pscore = evaluateParticle(particle, swarm)
        if pscore < particle["pbest"]:
            particle["pbestx"] = particle["px"]
            particle["pbesty"] = particle["py"]
            particle["pbest"] = pscore
        if pscore < swarm["gbest"]:
            swarm["gbest"] = pscore
            swarm["gbestx"] = particle["px"]
            swarm["gbesty"] = particle["py"]
    updateSwarm(swarm)
    # print(f"bgest:{swarm['gbest']:.{6}} x:{swarm['gbestx']:.{6}} y:{swarm['gbesty']:.{6}}")


def main():
    swarm = setupSwarm()
    print(f"target: {swarm['gold'][0]:.{6}} {swarm['gold'][1]:.{6}}")
    for i in range(200):
        runOptimisation(swarm)
        print(f"{swarm['gbest']:7.3f}")
    print(f"\nSolution x:{swarm['gbestx']:.{6}} ({swarm['gold'][0]:.{6}}) y:{swarm['gbesty']:.{6}} ({swarm['gold'][1]:.{6}})")


if __name__ == "__main__":
    # options, flags = gscript.parser()
    main()
