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

# --- Intro Primer ---
st.subheader("What is a Fuzzy Cognitive Map (FCM)?")
st.markdown("""
Fuzzy Cognitive Maps (FCMs) are visual tools that help you model how different concepts influence each other in a complex system. 
They’re especially useful when:
- The relationships are uncertain or subjective
- You're thinking about change over time
- You want to simulate how changes in one area might affect others

In this tool, you'll define a mental landscape, organize concepts into categories, link them, and simulate how they interact.
""")

# --- Define Mental Landscape ---
st.subheader("1. Identify Your Mental Landscape")
st.markdown("""
What system or experience are you trying to map? Some examples include:
- Launching a new MBA elective course
- Navigating a career transition
- Designing an organizational change initiative
- Improving student engagement in your class

Use this prompt to define your own focus area:
""")
mental_landscape = st.text_input("Describe the mental landscape you're mapping:", key="landscape")

# --- Define Concept Categories ---
st.subheader("2. Enter Concept Categories")
st.markdown("""
Concept categories help you organize your thinking. 
Here are some examples to get you started:
- Psychological Factors (confidence, motivation, anxiety)
- Student-Related Factors (engagement, preparedness, feedback)
- Course Development Factors (materials, objectives, assessments)
- Professional Development Factors
- Institutional Factors
- External Factors (market trends, industry relevance)

Enter 3–5 categories:
""")
categories_input = st.text_area("Enter one category per line:", height=150)
categories = [c.strip() for c in categories_input.split("\n") if c.strip() != ""]

if not categories:
    st.warning("Please enter at least one category to continue.")
    st.stop()

# --- Enter Concepts per Category ---
st.subheader("3. List Concepts Under Each Category")
st.markdown("Enter the individual variables or ideas that fall under each category.")
category_to_nodes = {}
for cat in categories:
    nodes_text = st.text_area(f"Concepts under '{cat}' (one per line):", key=f"concepts_{cat}")
    category_to_nodes[cat] = [n.strip() for n in nodes_text.split("\n") if n.strip() != ""]

node_list = [n for sublist in category_to_nodes.values() for n in sublist]

if len(node_list) < 10:
    st.warning("Please enter at least ten total concepts across categories.")
    st.stop()

# --- Define Relationships ---

st.subheader("4. Define Concept-to-Concept Influences")
st.markdown("""
Tell us how strongly each concept affects another.
- Choose from: **None**, **Low**, **Moderate**, **High**
- Positive means it reinforces, negative means it weakens the target
""")

influence_map = {
    "None": 0.0,
    "Low (+)": 0.3,
    "Moderate (+)": 0.6,
    "High (+)": 1.0,
    "Low (–)": -0.3,
    "Moderate (–)": -0.6,
    "High (–)": -1.0
}

edges = []
for i, source in enumerate(node_list):
    with st.container():
        st.markdown(f"<div style='border: 2px solid #ccc; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        st.markdown(f"### Influence Ratings for: {source}")
        col1, col2 = st.columns(2)
        for j, target in enumerate(node_list):
            if source != target:
                with [col1, col2][j % 2]:
                    st.markdown(f"**{source} ➡️ {target}**")
                    val = st.selectbox("Select influence:", options=list(influence_map.keys()), index=0, key=f"edge_{i}_{j}")
                    weight = influence_map[val]
                    if weight != 0.0:
                        edges.append((source, target, weight))
        st.markdown("</div>", unsafe_allow_html=True)

# --- Initial Activation ---
st.subheader("5. Set Initial Activation Levels")
st.markdown("""
Set how **active, present, or top-of-mind** each concept is in your current mental landscape.
Use values from **0.0 (inactive)** to **1.0 (highly active)**.
""")
initial_values = {}
for node in node_list:
    initial_values[node] = st.slider(f"{node}", 0.0, 1.0, 0.5, step=0.05)

# --- Build Graph and Simulate ---
G = nx.DiGraph()
G.add_nodes_from(node_list)
G.add_weighted_edges_from(edges)

steps = st.slider("Number of simulation steps:", 1, 10, 3)
damping = 0.5
current_values = initial_values.copy()

def squash(x):
    return max(0, min(1, x))

for _ in range(steps):
    updated_values = {}
    for node in G.nodes():
        influence = sum(current_values[pred] * G[pred][node]['weight'] for pred in G.predecessors(node))
        updated_values[node] = squash(current_values[node] + damping * influence)
    current_values = updated_values

# --- Final Concept Values ---
st.subheader("6. Final Concept Values After Simulation")
st.markdown("""
These values show which concepts became **more or less activated** after the influence of other concepts played out.
""")
st.dataframe(pd.DataFrame(current_values.items(), columns=["Concept", "Final Value"]))

# --- Visualize Graph ---
st.subheader("7. Visualize Your FCM")
fig, ax = plt.subplots(figsize=(18, 12))
pos = nx.spring_layout(G, seed=42, k=0.5)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1200, font_size=10, ax=ax)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='gray', font_size=9, ax=ax)
st.pyplot(fig)

# --- Leverage Point Simulation ---
st.subheader("8. Identify and Act on the Most Impactful Leverage Point")
st.markdown("""
Let’s identify your most **influential concept** — the one that affects the most others.
Then we’ll let you **adjust its influence** on any other concept and see the ripple effects.
""")

out_degrees = dict(G.out_degree())
if out_degrees:
    top_influencer = max(out_degrees, key=out_degrees.get)
    st.markdown(f"**Top Leverage Node:** {top_influencer} (influences {out_degrees[top_influencer]} others)")

    targets = [t for s, t, _ in edges if s == top_influencer]
    if targets:
        selected_target = st.selectbox("Select a target concept to modify influence toward:", targets)
        new_influence_val = st.selectbox("New influence level:", list(influence_map.keys()), index=0)
        new_weight = influence_map[new_influence_val]

        # Update the graph
        new_edges = [(s, t, w if not (s == top_influencer and t == selected_target) else new_weight)
                     for s, t, w in edges]
        G_new = nx.DiGraph()
        G_new.add_nodes_from(node_list)
        G_new.add_weighted_edges_from(new_edges)

        # Rerun simulation
        mod_values = initial_values.copy()
        for _ in range(steps):
            updated = {}
            for node in G_new.nodes():
                infl = sum(mod_values[pred] * G_new[pred][node]['weight'] for pred in G_new.predecessors(node))
                updated[node] = squash(mod_values[node] + damping * infl)
            mod_values = updated

        # Compare Results
        comparison = pd.DataFrame({
            "Concept": node_list,
            "Original": [round(current_values[n], 3) for n in node_list],
            "Modified": [round(mod_values[n], 3) for n in node_list]
        })
        comparison["Change"] = comparison["Modified"] - comparison["Original"]

        st.markdown("### Ripple Effect Analysis")
        st.markdown(f"How does modifying **{top_influencer} → {selected_target}** impact the system?")
        st.dataframe(comparison)

        st.markdown("""
        **Insights to Explore:**
        - Which downstream concepts increased or decreased the most?
        - Did changing this one connection improve activation of key areas?
        - What new tradeoffs or tensions emerged?
        """)

# --- Footer ---
st.markdown("<hr><p style='text-align:center'>Created for the Adaptive Leadership course</p>", unsafe_allow_html=True)
