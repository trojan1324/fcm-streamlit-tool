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

# --- Scenario Selector ---
with st.expander("💡 Or start with a pre-built scenario"):
    scenario = st.selectbox("Choose a scenario to explore:", ["None", "Navigating Impostor Syndrome", "Managing Up, Down, and Sideways", "Transitioning from Contributor to Manager"])
    preset_nodes, preset_edges = [], []
    if scenario == "Navigating Impostor Syndrome":
        preset_nodes = [
            "Impostor feelings", "Peer comparison", "Perfectionism", "Confidence", "Feedback seeking",
            "Mentoring support", "Reframing failure", "Participation in class", "Experimentation", "Belonging"
        ]
        preset_edges = [
            ("Peer comparison", "Impostor feelings", 1.0),
            ("Perfectionism", "Impostor feelings", 0.6),
            ("Impostor feelings", "Confidence", -1.0),
            ("Confidence", "Participation in class", 0.8),
            ("Confidence", "Experimentation", 0.6),
            ("Mentoring support", "Confidence", 0.6),
            ("Reframing failure", "Confidence", 0.6),
            ("Feedback seeking", "Confidence", 0.4),
            ("Belonging", "Confidence", 0.5),
            ("Participation in class", "Belonging", 0.5),
        ]
    elif scenario == "Managing Up, Down, and Sideways":
        preset_nodes = [
            "Clarity of goals", "Trust with supervisor", "Team cohesion", "Lateral communication",
            "Influence skills", "Conflicting priorities", "Feedback loops", "Strategic alignment",
            "Reputation", "Psychological safety"
        ]
        preset_edges = [
            ("Clarity of goals", "Strategic alignment", 0.8),
            ("Trust with supervisor", "Feedback loops", 0.6),
            ("Lateral communication", "Team cohesion", 0.7),
            ("Team cohesion", "Psychological safety", 0.8),
            ("Feedback loops", "Reputation", 0.6),
            ("Influence skills", "Trust with supervisor", 0.5),
            ("Conflicting priorities", "Strategic alignment", -0.7),
            ("Strategic alignment", "Reputation", 0.7),
        ]
    elif scenario == "Transitioning from Contributor to Manager":
        preset_nodes = [
            "Desire to stay hands-on", "Delegation skills", "Trust in team", "Micromanagement",
            "Clarity of role", "Team development", "Communication skills", "Manager identity",
            "Peer support", "Feedback seeking", "Strategic thinking", "Time management",
            "Imposter syndrome", "Perceived effectiveness", "Team performance"
        ]
        preset_edges = [
            ("Desire to stay hands-on", "Micromanagement", 0.7),
            ("Micromanagement", "Trust in team", -0.8),
            ("Delegation skills", "Trust in team", 0.6),
            ("Trust in team", "Team performance", 0.7),
            ("Team performance", "Perceived effectiveness", 0.8),
            ("Perceived effectiveness", "Manager identity", 0.6),
            ("Feedback seeking", "Manager identity", 0.5),
            ("Imposter syndrome", "Feedback seeking", -0.5),
            ("Strategic thinking", "Clarity of role", 0.7),
            ("Clarity of role", "Manager identity", 0.6),
            ("Manager identity", "Delegation skills", 0.7),
            ("Time management", "Micromanagement", -0.5),
            ("Communication skills", "Trust in team", 0.6),
        ]

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

# Use preset nodes and edges if scenario selected, otherwise allow manual input (in the next development steps)
if preset_nodes:
    st.subheader("Scenario Concepts")
    st.markdown("These are the core concepts defined in the selected scenario:")
    for node in preset_nodes:
        st.markdown(f"- {node}")

    st.subheader("Visualizing the Scenario")
    G = nx.DiGraph()
    G.add_nodes_from(preset_nodes)
    G.add_weighted_edges_from(preset_edges)

    fig, ax = plt.subplots(figsize=(12, 10))
    pos = nx.spring_layout(G, k=0.5, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue", alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold")
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True, width=2, alpha=0.5)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(i, j): f"{w:.1f}" for i, j, w in preset_edges}, font_size=8)
    plt.title("Fuzzy Cognitive Map", fontsize=16)
    plt.axis("off")
    st.pyplot(fig)

    st.subheader("🧠 Identify Leverage Points")
    out_strength = G.out_degree(weight='weight')
    most_influential = sorted(out_strength, key=lambda x: out_strength[x], reverse=True)[0]
    st.markdown(f"**Most influential concept:** `{most_influential}`")

    options = [n for n in preset_nodes if n != most_influential]
    target_node = st.selectbox("Which concept do you want to adjust its influence on?", options)
    new_weight = st.slider("Adjust influence strength:", -1.0, 1.0, 0.5, step=0.1)

    st.markdown("---")
    st.markdown("### 🌀 Ripple Effect Analysis")
    st.markdown(f"You increased/decreased `{most_influential}`'s impact on `{target_node}` to `{new_weight}`.")
    st.markdown("This change would affect not just the target concept but also other concepts **downstream** through the system. Depending on feedback loops and connectivity, it may amplify or dampen other areas.")
    st.markdown("Students should explore questions like:")
    st.markdown("- How direct is the impact of this change?")
    st.markdown("- What other concepts are indirectly influenced?")
    st.markdown("- Does this adjustment create more clarity or unintended friction?")

    st.success("Use this analysis to experiment with leverage and complexity. The goal is to uncover where small shifts yield systemic improvement.")
else:
    st.info("Select a scenario or build your own FCM (feature coming soon)")
