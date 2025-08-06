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

if len(node_list) < 2:
    st.warning("Please enter at least ten total concepts across categories.")
    st.stop()

# --- Define Relationships ---

st.subheader("4. Define Concept-to-Concept Influences")
st.markdown("""
Tell us how strongly each concept affects another.
- Use values between **-1.0 and +1.0**
- Use **increments of 0.1**
- Leave blank if there's no direct influence

Tip: Positive = reinforcing, Negative = reducing
""")

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
                    val = st.text_input("Weight (-1.0 to 1.0):", key=f"edge_{i}_{j}")
                    try:
                        weight = float(val)
                        if -1.0 <= weight <= 1.0 and weight != 0.0:
                            edges.append((source, target, weight))
                    except:
                        continue
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"### Rating: {source}")
    col1, col2, col3 = st.columns(3)
    for j, target in enumerate(node_list):
        if source != target:
            with [col1, col2, col3][j % 3]:
                st.markdown(f"**{source} ➡️ {target}**")
                val = st.text_input("Weight (-1.0 to 1.0):", key=f"edge_{i}_{j}")
                try:
                    weight = float(val)
                    if -1.0 <= weight <= 1.0 and weight != 0.0:
                        edges.append((source, target, weight))
                except:
                    continue

# --- Initial Activation ---
st.subheader("5. Set Initial Activation Levels")
st.markdown("""
Here you're setting the **starting activation level** of each concept. This represents how present, important, or top-of-mind this factor is for you in the current mental landscape you're analyzing. For example, if you're feeling highly motivated, you might set 'Motivation' to 1.0. If 'Institutional Support' feels absent or irrelevant, you might set it lower, like 0.2.

- Use values between **0.0 (low)** and **1.0 (high)**
- You’ll see how these values evolve during the simulation
""")
initial_values = {}
for node in node_list:
    initial_values[node] = st.slider(f"{node}", 0.0, 1.0, 0.5, step=0.05)

# --- Build Graph ---
G = nx.DiGraph()
G.add_nodes_from(node_list)
G.add_weighted_edges_from(edges)

# --- Propagation ---
st.subheader("6. Run the Simulation")
st.markdown("""
Now we'll simulate how changes spread through your system.

- The system runs multiple rounds ("steps") to show how each concept is influenced by others over time
- The more steps you run, the more chances indirect or reinforcing effects have to show up
- Values are normalized to stay between 0 and 1 during propagation

Try different step counts and observe how concepts evolve.
""")

steps = st.slider("Number of simulation steps:", 1, 10, 3)
current_values = initial_values.copy()

# Define bounded linear squashing function
def squash(x):
    return max(0, min(1, x))

damping = 0.5  # Controls how fast influence spreads
for _ in range(steps):
    updated_values = {}
    for node in G.nodes():
        influence = sum(current_values[pred] * G[pred][node]['weight'] for pred in G.predecessors(node))
        updated_values[node] = squash(current_values[node] + damping * influence)
    current_values = updated_values

# --- Show Final Values ---
st.subheader("7. What Changed? Final Concept Values After Simulation")
st.markdown("""
This table shows the final activation level of each concept **after the simulation has completed** — meaning, after the influence of related concepts has been applied over several rounds.

- A **higher number** (closer to 1.0) means the concept became more prominent, active, or impactful as other factors pushed it upward.
- A **lower number** (closer to 0.0) means it became less influential, possibly because other factors suppressed it.

Use this to answer questions like:
- Which concepts became stronger over time?
- Which concepts were diminished or stayed stagnant?
- How did indirect influences change the system compared to my initial inputs?
""")
st.dataframe(pd.DataFrame(current_values.items(), columns=["Concept", "Final Value"]))

# --- Draw Graph ---
st.subheader("8. Visualize Your FCM")
st.markdown("""
This is a visual representation of the map you’ve built:
- **Circles** represent your concepts
- **Arrows** represent the direction and strength of influence
- **Arrow labels** show the weight of the relationship

Tips:
- Densely connected maps may look messy — that’s okay. Focus on identifying clusters or key influencers.
- You can also use the summary below to interpret key drivers and bottlenecks in your system.
""")
fig, ax = plt.subplots(figsize=(18, 12))
pos = nx.spring_layout(G, seed=42, k=0.5)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1200, font_size=10, ax=ax)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='gray', font_size=9, ax=ax)
st.pyplot(fig)

# --- Graph Summary ---

st.subheader("9. Graph Summary: What Can You Learn From This Map?")
if len(edges) >= 5:
    st.markdown("""
    Here are a few analytical takeaways to help interpret your FCM:

    - **Most Influential Concepts (Outbound)** – Concepts that influence the most others:
    """)

    try:
        out_degrees = dict(G.out_degree())
        top_out = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        for node, degree in top_out:
            st.write(f"🔹 {node}: influences {degree} other concept(s)")

        st.markdown("""
        - **Most Affected Concepts (Inbound)** – Concepts that are influenced by many others:
        """)

        in_degrees = dict(G.in_degree())
        top_in = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        for node, degree in top_in:
            st.write(f"🔸 {node}: influenced by {degree} other concept(s)")

        st.markdown("""
        - **Loops and Feedback** – If any concepts influence each other back and forth, you may be modeling a **feedback loop**, which is important for understanding reinforcement or delay in systems.
        - **Isolated Nodes** – Concepts without any links may need further thinking: Are they disconnected by design or missing an influence?

        Use these cues to reflect on what your map reveals about the dynamics in your mental landscape.
        """)

    except Exception as e:
        st.warning("Graph summary could not be generated due to a data issue. Please double-check your concept connections.")
else:
    st.info("Your map has fewer than 5 relationships. Add more connections to generate a meaningful summary.")

# --- Ripple Effect Simulation ---

st.subheader("11. Explore the Ripple Effect of a Change")
st.markdown("""
Use this section to explore how modifying a **single relationship** between concepts changes the outcome of your map.
Select a source and target concept, modify the influence weight, and compare the final results.
""")

selected_source = st.selectbox("Choose the concept that influences: (source)", node_list, key="ripple_source")
candidate_targets = [n for n in node_list if n != selected_source]
selected_target = st.selectbox("Choose the concept that is influenced: (target)", candidate_targets, key="ripple_target")
new_weight = st.slider("Set new influence value (-1.0 to 1.0):", -1.0, 1.0, 0.0, step=0.1, key="ripple_weight")

# Copy and modify edge list
modified_edges = [(s, t, w) if not (s == selected_source and t == selected_target) else (s, t, new_weight)
                  for (s, t, w) in edges]
edge_exists = any((s == selected_source and t == selected_target) for (s, t, w) in edges)
if not edge_exists and new_weight != 0.0:
    modified_edges.append((selected_source, selected_target, new_weight))

# Build modified graph
G_mod = nx.DiGraph()
G_mod.add_nodes_from(node_list)
G_mod.add_weighted_edges_from(modified_edges)

# Simulate original and modified
original_values = current_values.copy()
mod_values = initial_values.copy()

for _ in range(steps):
    new_mod = {}
    for node in G_mod.nodes():
        infl = sum(mod_values[pred] * G_mod[pred][node]['weight'] for pred in G_mod.predecessors(node))
        new_mod[node] = squash(mod_values[node] + damping * infl)
    mod_values = new_mod

# Compare
st.markdown("""
**Comparison of Final Concept Values (Original vs. Modified)**
- Green = value increased due to your change
- Red = value decreased
""")

comparison_df = pd.DataFrame({
    "Concept": node_list,
    "Original": [round(original_values[n], 3) for n in node_list],
    "Modified": [round(mod_values[n], 3) for n in node_list]
})
comparison_df["Change"] = comparison_df["Modified"] - comparison_df["Original"]

st.dataframe(comparison_df.style.applymap(
    lambda x: 'background-color: #d1e7dd' if x > 0 else ('background-color: #f8d7da' if x < 0 else ''),
    subset=["Change"]
))

# --- Download as Image ---
buffer = io.BytesIO()
fig.savefig(buffer, format='png')
buffer.seek(0)
b64 = base64.b64encode(buffer.read()).decode()
st.markdown(f'<a href="data:image/png;base64,{b64}" download="fcm_graph.png">Download Graph as PNG</a>', unsafe_allow_html=True)

# --- Download as CSV ---
df_nodes = pd.DataFrame.from_dict(current_values, orient='index', columns=['Final Value'])
df_nodes.index.name = 'Concept'
df_edges = pd.DataFrame(edges, columns=['Source', 'Target', 'Weight'])

csv_buffer_nodes = io.StringIO()
csv_buffer_edges = io.StringIO()
df_nodes.to_csv(csv_buffer_nodes)
df_edges.to_csv(csv_buffer_edges)

b64_nodes = base64.b64encode(csv_buffer_nodes.getvalue().encode()).decode()
b64_edges = base64.b64encode(csv_buffer_edges.getvalue().encode()).decode()

st.subheader("10. Download Your Map Data")
st.markdown(f'<a href="data:file/csv;base64,{b64_nodes}" download="fcm_nodes.csv">Download Final Values (CSV)</a>', unsafe_allow_html=True)
st.markdown(f'<a href="data:file/csv;base64,{b64_edges}" download="fcm_edges.csv">Download Connections (CSV)</a>', unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center'>Created for the Adaptive Leadership course</p>", unsafe_allow_html=True)
