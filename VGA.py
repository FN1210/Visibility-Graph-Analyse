import streamlit as st
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm

# ---------- App Config ----------
st.set_page_config(page_title="Visibility Graph Analyse", layout="centered")
st.title("🌐 Visibility Graph Analyse")

# ---------- Datei-Upload ----------
uploaded_file = st.file_uploader("📤 Lade deine RR-Intervall-Datei (.txt) hoch", type=["txt"])

# ---------- Visibility Graph Funktionen ----------
def visibility_graph_fast(ts):
    G = nx.Graph()
    N = len(ts)
    G.add_nodes_from(range(N))
    for i in range(N):
        t_i, y_i = i, ts[i]
        max_slope = -np.inf
        for j in range(i+1, N):
            t_j, y_j = j, ts[j]
            slope = (y_j - y_i) / (t_j - t_i)
            visible = True
            for k in range(i+1, j):
                t_k, y_k = k, ts[k]
                y_interp = y_i + slope * (t_k - t_i)
                if y_k >= y_interp:
                    visible = False
                    break
            if visible:
                G.add_edge(i, j)
    return G

def plot_visibility_graph(G):
    degrees = [deg for _, deg in G.degree()]
    if len(degrees) > 0:
        plt.figure(figsize=(8, 4), facecolor='#000')
        plt.hist(degrees, bins=range(min(degrees), max(degrees)+1), alpha=0.8, color='#6DCFF6', edgecolor='white')
        plt.title("Degree Distribution of Visibility Graph", color='white')
        plt.xlabel("Degree", color='white')
        plt.ylabel("Frequency", color='white')
        plt.grid(True, color='#555', linestyle='--', linewidth=0.5)
        plt.gca().tick_params(colors='white')
        plt.gca().spines['bottom'].set_color('white')
        plt.gca().spines['left'].set_color('white')
        st.pyplot(plt.gcf())
        plt.close()
    else:
        st.warning("Nicht genug Knoten im Visibility Graph für eine Verteilung.")

# ---------- Hauptlogik ----------
if uploaded_file is not None:
    rr_lines = uploaded_file.read().decode("utf-8").splitlines()
    rr_intervals = np.array([float(line.strip()) for line in rr_lines if line.strip()])

    with st.spinner("Erzeuge Visibility Graph..."):
        G = visibility_graph_fast(rr_intervals[:1000])  # Limitierung für Performance

    plot_visibility_graph(G)
else:
    st.info("Bitte lade eine .txt-Datei mit RR-Intervallen hoch (eine Zahl pro Zeile).")
