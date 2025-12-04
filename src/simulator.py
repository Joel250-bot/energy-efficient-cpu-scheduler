# src/simulator.py
import json, argparse
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0
    remaining: int = field(init=False)
    start_times: List[int] = field(default_factory=list)
    finish_time: Optional[int] = None

    def __post_init__(self):
        self.remaining = self.burst

class Simulator:
    def __init__(self, processes: List[Process], sleep_threshold=5):
        self.procs = sorted(processes, key=lambda p: p.arrival)
        self.time = 0
        self.ready = []
        self.finished = []
        self.timeline = []

        # energy params
        self.P_active = 5.0
        self.P_idle = 1.0
        self.P_sleep = 0.2
        self.T_wakeup = 2
        self.E_wakeup = 2.0
        self.sleep_threshold = sleep_threshold

    def _add_arrivals(self):
        while self.procs and self.procs[0].arrival <= self.time:
            p = self.procs.pop(0)
            self.ready.append(p)

    def _record(self, state, pid=None):
        self.timeline.append((self.time, state, pid))

    def run(self):
        energy = 0.0
        while self.procs or self.ready:
            self._add_arrivals()

            if self.ready:
                # Simple energy-performance heuristic
                chosen = min(
                    self.ready,
                    key=lambda p: 0.7*(p.remaining * self.P_active) + 0.3*p.remaining
                )

                self._record("ACTIVE", chosen.pid)

                if chosen.burst == chosen.remaining:
                    chosen.start_times.append(self.time)

                chosen.remaining -= 1
                energy += self.P_active
                self.time += 1

                if chosen.remaining == 0:
                    chosen.finish_time = self.time
                    self.finished.append(chosen)
                    self.ready.remove(chosen)

            else:
                # No ready processes → idle or sleep decision
                if self.procs:
                    gap = self.procs[0].arrival - self.time
                else:
                    gap = float("inf")

                if gap >= self.sleep_threshold:
                    self._record("SLEEP", None)
                    dt = min(gap, self.sleep_threshold)
                    energy += dt * self.P_sleep
                    self.time += dt
                    energy += self.E_wakeup
                    self.time += self.T_wakeup
                else:
                    self._record("IDLE", None)
                    energy += self.P_idle
                    self.time += 1

            self._add_arrivals()

        total_turn = sum(p.finish_time - p.arrival for p in self.finished)
        total_wait = sum(
            (p.finish_time - p.arrival - p.burst) for p in self.finished
        )
        n = len(self.finished)

        metrics = {
            "avg_turnaround": total_turn / n if n else 0,
            "avg_waiting": total_wait / n if n else 0,
            "total_energy": energy,
            "process_count": n
        }

        return metrics, self.timeline, self.finished

def load_processes(path):
    with open(path, "r") as f:
        arr = json.load(f)
    return [
        Process(
            pid=str(i + 1),
            arrival=p["arrival"],
            burst=p["burst"],
            priority=p.get("priority", 0),
        )
        for i, p in enumerate(arr)
    ]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--sleep", type=int, default=5)
    args = parser.parse_args()

    procs = load_processes(args.input)
    sim = Simulator(procs, sleep_threshold=args.sleep)
    metrics, timeline, finished = sim.run()

    print("Metrics:", metrics)
    pandas_report = pd.DataFrame([metrics])
    pandas_report.to_csv("metrics.csv", index=False)
