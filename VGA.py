import streamlit as st
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import linregress
import pandas as pd

st.title("RR Visibility Graph Analyzer")

# Upload RR data
uploaded_file = st.file_uploader("Upload RR data (CSV/TXT)", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        rr_data = pd.read_csv(uploaded_file, header=None).squeeze("columns")
    except Exception:
        rr_data = pd.read_csv(uploaded_file, delim_whitespace=True, header=None).squeeze("columns")

    ts = rr_data.values

    # Optimierte Sichtbarkeitsgraph-Funktion (keine extra Libs)
    def compute_visibility_graph(ts):
        G = nx.Graph()
        n = len(ts)
        for i in range(n):
            G.add_node(i, value=ts[i])
            for j in range(i+1, n):
                dy = ts[j] - ts[i]
                dx = j - i
                visible = True
                for k in range(i+1, j):
                    if ts[k] > ts[i] + dy * ((k - i) / dx):
                        visible = False
                        break
                if visible:
                    G.add_edge(i, j)
        return G

    G = compute_visibility_graph(ts)

    # (b) Zeitreihe
    fig1, ax1 = plt.subplots()
    ax1.plot(ts, color='black')
    ax1.set_title("(b) RR Time Series")
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("Magnitude")
    st.pyplot(fig1)

    # (a) Sichtbarkeitsgraph
    fig2, ax2 = plt.subplots()
    pos = nx.spring_layout(G, seed=42, k=0.1, iterations=20)
    degrees = [G.degree(n) for n in G.nodes()]
    nx.draw(G, pos, node_size=20, node_color=degrees, cmap=plt.cm.viridis, ax=ax2, with_labels=False)
    ax2.set_title("(a) Visibility Graph")
    st.pyplot(fig2)

    # (c) k vs M Plot mit Linear Fit
    k = np.array([G.degree(n) for n in G.nodes()])
    M = np.array([ts[n] for n in G.nodes()])
    slope, intercept, r_value, p_value, std_err = linregress(M, k)

    fig3, ax3 = plt.subplots()
    ax3.scatter(M, k, color='black', s=10, label='Data')
    ax3.plot(M, intercept + slope*M, color='red', label='Linear fit')
    ax3.set_xlabel("Magnitude (M)")
    ax3.set_ylabel("Connectivity degree (k)")
    ax3.set_title("(c) k vs M with Linear Fit")
    ax3.legend()
    st.pyplot(fig3)

    st.markdown(f"**Average Degree:** {np.mean(k):.2f}")
    st.markdown(f"**Average Path Length:** {nx.average_shortest_path_length(G):.2f}" if nx.is_connected(G) else "Graph is not connected.")
else:
    st.info("Please upload a file to begin.")
