# Energy-Efficient CPU Scheduler

This project implements an energy-aware CPU scheduling simulation designed for mobile and embedded systems.  
It reduces energy consumption while maintaining performance.

## How to Run

1. Activate virtual environment:
   - Windows:   .\venv\Scripts\activate

2. Install dependencies:
   pip install -r requirements.txt

3. Run the simulator:
   python src/simulator.py -i data/input.json --sleep 5

## Project Structure
- src/               → Simulator code  
- data/              → Input JSON files  
- docs/              → Report and diagrams  
- README.md          → Project info  
- requirements.txt   → Python dependencies  
- .gitignore         → Ignore unnecessary files  

Feature branch for energy heuristic.
