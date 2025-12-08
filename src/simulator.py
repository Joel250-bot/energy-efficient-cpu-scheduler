# src/simulator.py
import json
import argparse
from dataclasses import dataclass, field
from typing import List, Optional
import matplotlib.pyplot as plt
import pandas as pd

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    remaining: int = field(init=False)
    start_times: List[int] = field(default_factory=list)
    finish_time: Optional[int] = None

    def __post_init__(self):
        self.remaining = self.burst


class Simulator:
    def __init__(self, processes: List[Process], sleep_threshold=5):
        self.procs = sorted(processes, key=lambda p: p.arrival)
        self.ready = []
        self.time = 0
        self.finished = []
        self.sleep_threshold = sleep_threshold

        # Power model
        self.P_active = 5.0
        self.P_idle = 1.0
        self.P_sleep = 0.2
        self.T_wakeup = 2
        self.E_wakeup = 2.0

    def add_arrivals(self):
        while self.procs and self.procs[0].arrival <= self.time:
            self.ready.append(self.procs.pop(0))

    def run(self):
        energy = 0.0

        while self.procs or self.ready:
            self.add_arrivals()

            if self.ready:
                # Energy-efficient selection
                chosen = min(
                    self.ready,
                    key=lambda p: 0.7 * (p.remaining * self.P_active) + 0.3 * p.remaining
                )
                
                if chosen.remaining == chosen.burst:
                    chosen.start_times.append(self.time)

                chosen.remaining -= 1
                energy += self.P_active
                self.time += 1

                if chosen.remaining == 0:
                    chosen.finish_time = self.time
                    self.finished.append(chosen)
                    self.ready.remove(chosen)

            else:
                # No ready processes → Idle or Sleep
                next_arrival = self.procs[0].arrival - self.time if self.procs else float("inf")

                if next_arrival >= self.sleep_threshold:
                    # Sleep mode
                    energy += self.P_sleep * self.sleep_threshold
                    self.time += self.sleep_threshold

                    # Wakeup energy + delay
                    energy += self.E_wakeup
                    self.time += self.T_wakeup
                else:
                    # Idle mode
                    energy += self.P_idle
                    self.time += 1

            self.add_arrivals()

        # Metrics
        total_turn = sum(p.finish_time - p.arrival for p in self.finished)
        total_wait = sum((p.finish_time - p.arrival - p.burst) for p in self.finished)
        n = len(self.finished)

        metrics = {
            "avg_turnaround": total_turn / n if n else 0,
            "avg_waiting": total_wait / n if n else 0,
            "total_energy": energy,
            "process_count": n,
        }

        return metrics, self.finished


def load_processes(path):
    with open(path, "r") as f:
        data = json.load(f)

    return [
        Process(
            pid=str(i + 1),
            arrival=p["arrival"],
            burst=p["burst"]
        )
        for i, p in enumerate(data)
    ]


def generate_plots(metrics):
    # Energy plot
    plt.figure()
    plt.plot(["Energy"], [metrics["total_energy"]], marker="o")
    plt.title("Total Energy Consumption")
    plt.savefig("energy_plot.png")
    plt.close()

    # Turnaround plot
    plt.figure()
    plt.plot(["Turnaround"], [metrics["avg_turnaround"]], marker="o")
    plt.title("Average Turnaround Time")
    plt.savefig("turnaround_plot.png")
    plt.close()

    # Waiting plot
    plt.figure()
    plt.plot(["Waiting"], [metrics["avg_waiting"]], marker="o")
    plt.title("Average Waiting Time")
    plt.savefig("waiting_plot.png")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--sleep", type=int, default=5)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    procs = load_processes(args.input)
    sim = Simulator(procs, sleep_threshold=args.sleep)
    metrics, finished = sim.run()

    print("Metrics:", metrics)

    if args.plot:
        generate_plots(metrics)
        print("Plots saved.")
