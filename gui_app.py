#gui 
import streamlit as st
import json
import pandas as pd
from src.simulator import load_processes, Simulator, generate_plots

st.set_page_config(page_title="Energy Efficient CPU Scheduler", layout="wide")

st.title("⚡ Energy-Efficient CPU Scheduling Simulator")
st.write("Simulate CPU execution using energy-aware scheduling for mobile/embedded systems.")

st.sidebar.header("Controls")

uploaded_file = st.sidebar.file_uploader("Upload input.json", type="json")
sleep_threshold = st.sidebar.number_input("Sleep Threshold", min_value=1, max_value=20, value=5)
run_btn = st.sidebar.button("Run Simulation")

if run_btn:
    if uploaded_file is None:
        st.error("Please upload input.json first.")
    else:
        data = json.load(uploaded_file)

        with open("uploaded_input.json", "w") as f:
            json.dump(data, f)

        procs = load_processes("uploaded_input.json")
        sim = Simulator(procs, sleep_threshold)

        metrics, finished = sim.run()

        st.subheader("📊 Metrics")
        metrics_df = pd.DataFrame([metrics])
        st.dataframe(metrics_df)

        generate_plots(metrics)

        col1, col2, col3 = st.columns(3)

        col1.image("energy_plot.png", caption="Total Energy Used")
        col2.image("turnaround_plot.png", caption="Avg Turnaround")
        col3.image("waiting_plot.png", caption="Avg Waiting")

        st.subheader("📘 Finished Processes")
        fp = [{
            "PID": p.pid,
            "Arrival": p.arrival,
            "Burst": p.burst,
            "Finish Time": p.finish_time
        } for p in finished]

        st.dataframe(pd.DataFrame(fp))

        st.success("Simulation completed!")
