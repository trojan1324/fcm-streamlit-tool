import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

# --- Page Config ---
st.set_page_config(page_title="FCM Tool", layout="wide")

# --- Header ---
st.markdown("""
<h1 style='text-align: center;'>Adaptive Leadership: Navigating Complexity & Change</h1>
<h3 style='text-align: center; color: gray;'>Fuzzy Cognitive Mapping Tool</h3>
<hr>
""", unsafe_allow_html=True)

# --- Instructions ---
st.markdown("""
**Instructions:**
1. Add concepts (nodes) below — e.g., "Sleep Quality", "Mentorship"
2. Define how each concept influences another (positive or negative)
3. Adjust initial values and simulate ripple effects
4. Download your map as an image or spreadsheet
""")

# --- Input Nodes ---
st.subheader("1. Define Your Concepts")
nodes = st.text_area("Enter one concept per line (10–20 recommended):", height=200)
node_list = [n.strip() for n in nodes.split("\n") if n.strip() != ""]

if len(node_list) < 2:
    st.warning("Please enter at least two concepts to proceed.")
    st.stop()

# --- Input Edges ---
st.subheader("2. Define Relationships Between Concepts")
st.markdown("Enter how one concept affects another. Positive = reinforcing. Negative = reducing.")

edges = []
states = {}

for i, source in enumerate(node_list):
    for j, target in enumerate(node_list):
        if source != target:
            col1, col2 = st.columns([3, 1])
            with col1:
                label = f"How does '{source}' affect '{target}'? (-1 to 1, or leave blank)"
                val = st.text_input(label, key=f"edge_{i}_{j}")
            with col2:
                try:
                    weight = float(val)
                    if weight != 0.0:
                        edges.append((source, target, weight))
                except:
                    continue

# --- Initial Activation ---
st.subheader("3. Set Initial Activation Levels")
st.markdown("Set the starting importance/activation level for each concept (0 to 1):")
initial_values = {}
for node in node_list:
    initial_values[node] = st.slider(f"{node}", 0.0, 1.0, 0.5, step=0.05)

# --- Build Graph ---
G = nx.DiGraph()
G.add_nodes_from(node_list)
G.add_weighted_edges_from(edges)

# --- Propagate Activation ---
st.subheader("4. Simulate Influence Propagation")
steps = st.slider("How many steps should the simulation run?", 1, 10, 3)
current_values = initial_values.copy()

for step in range(steps):
    new_values = current_values.copy()
    for node in G.nodes():
        influence = 0
        for pred in G.predecessors(node):
            influence += current_values[pred] * G[pred][node]['weight']
        new_values[node] = max(0, min(1, current_values[node] + influence))
    current_values = new_values

# --- Display Updated Values ---
st.subheader("5. Final Concept Values After Simulation")
st.dataframe(pd.DataFrame(current_values.items(), columns=["Concept", "Final Value"]))

# --- Draw Graph ---
st.subheader("6. Visualize FCM Graph")
fig, ax = plt.subplots(figsize=(10, 6))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, ax=ax)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='gray', ax=ax)
st.pyplot(fig)

# --- Download as Image ---
buffer = io.BytesIO()
fig.savefig(buffer, format='png')
buffer.seek(0)
b64 = base64.b64encode(buffer.read()).decode()
href_img = f'<a href="data:image/png;base64,{b64}" download="fcm_graph.png">Download Graph as PNG</a>'
st.markdown(href_img, unsafe_allow_html=True)

# --- Download as CSV ---
st.subheader("7. Download Map Data")

# Nodes CSV
df_nodes = pd.DataFrame.from_dict(current_values, orient='index', columns=['Final Value'])
df_nodes.index.name = 'Concept'

# Edges CSV
df_edges = pd.DataFrame(edges, columns=['Source', 'Target', 'Weight'])

csv_buffer_nodes = io.StringIO()
csv_buffer_edges = io.StringIO()
df_nodes.to_csv(csv_buffer_nodes)
df_edges.to_csv(csv_buffer_edges)

b64_nodes = base64.b64encode(csv_buffer_nodes.getvalue().encode()).decode()
b64_edges = base64.b64encode(csv_buffer_edges.getvalue().encode()).decode()

st.markdown(f'<a href="data:file/csv;base64,{b64_nodes}" download="fcm_nodes.csv">Download Final Values (CSV)</a>', unsafe_allow_html=True)
st.markdown(f'<a href="data:file/csv;base64,{b64_edges}" download="fcm_edges.csv">Download Connections (CSV)</a>', unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center'>Created for the Adaptive Leadership course</p>", unsafe_allow_html=True)
