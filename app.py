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

- The system will run multiple rounds ("steps") to show how each concept is affected by others over time
- This lets you see how your system *naturally evolves*, based on your relationships and initial values

Adjust the number of steps below and watch how values change:
""")
steps = st.slider("Number of simulation steps:", 1, 10, 3)
current_values = initial_values.copy()

for step in range(steps):
    new_values = current_values.copy()
    for node in G.nodes():
        influence = 0
        for pred in G.predecessors(node):
            influence += current_values[pred] * G[pred][node]['weight']
        new_values[node] = max(0, min(1, current_values[node] + influence))
    current_values = new_values

# --- Show Final Values ---
st.subheader("7. What Changed? Final Concept Values After Simulation")
st.markdown("""
Here are the final values for each concept *after* the simulation ran.

- A higher number means that concept became more influential or activated as a result of the system interactions.
- A lower number means it was reduced or suppressed.

Use this to see which parts of your system gain or lose importance over time.
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
st.markdown("""
Here are a few analytical takeaways to help interpret your FCM:

- **Most Influential Concepts (Outbound)** – Concepts that influence the most others:
""")

try:
    top_out = sorted(G.out_degree(), key=lambda x: G.out_degree(x), reverse=True)[:5]
    for node in top_out:
        st.write(f"🔹 {node}: influences {G.out_degree(node)} other concept(s)")

    st.markdown("""
- **Most Affected Concepts (Inbound)** – Concepts that are influenced by many others:
""")

    top_in = sorted(G.in_degree(), key=lambda x: G.in_degree(x), reverse=True)[:5]
    for node in top_in:
        st.write(f"🔸 {node}: influenced by {G.in_degree(node)} other concept(s)")

    st.markdown("""
- **Loops and Feedback** – If any concepts influence each other back and forth, you may be modeling a **feedback loop**, which is important for understanding reinforcement or delay in systems.
- **Isolated Nodes** – Concepts without any links may need further thinking: Are they disconnected by design or missing an influence?

Use these cues to reflect on what your map reveals about the dynamics in your mental landscape.
""")
except Exception as e:
    st.warning("Graph summary could not be generated due to a data issue. Please double-check your concept connections.")

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
