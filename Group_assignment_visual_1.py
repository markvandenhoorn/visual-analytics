import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Group assignment Visual Analytics for Big Data: Mini-Challenge 3
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ::lucide:arrow-big-up:: Ideas to explore
    - Basic; who communicates over what
    - Timeline messages? check if posible, saw timestamp from 2040 haha
    - We should observe rising tensions among fisher -> maybe also sentiment analyises on text messages?
    - Maybe do some sort of clustering analyises to identify "These efforts revealed a story involving high-level Oceanus officials, Sailor Shift’s team, local influential families, and local conservationist group The Green Guardians, pointing towards a story of corruption and manipulation." -> text from assignment description
    - Maybe we can do some network measure how close one person/ organiseation/ other entity? is to another ->
    -Closeness Centrality/ Degree of Separation/ Network proximity measures/ Shortest Path measure
    """)
    return


@app.cell
def _():
    #Import packages 
    import marimo as mo #to marimo document 
    import json
    from networkx.readwrite import json_graph
    import networkx as nx
    import os #setting working directionary 
    import matplotlib.pyplot as plt #to plot 
    from collections import Counter
    import pandas as pd
    import altair as alt
    return Counter, alt, json, json_graph, mo, nx, os, pd, plt


@app.cell
def _(os):
    os.chdir(r"MC3-data") #set working directionary
    return


@app.cell
def _(json, json_graph):
    # import data
    with open("MC3_schema.json", "r") as schema_file:
        schema = json.load(schema_file)

    with open("MC3_graph.json", "r") as graph_file:
        graph_data = json.load(graph_file)

    G = json_graph.node_link_graph(graph_data)

    #check nodes & edges
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    return (G,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explore data
    """)
    return


@app.cell
def _(G):
    #check data structure 
    list(G.nodes(data=True))[:5] #check how node looks

    return


@app.cell
def _(G):
    for u, v, attrs in list(G.edges(data=True))[:10]:
        print(f"{u} -> {v}, attributes: {attrs}") #check first 10 edges 
    return


@app.cell
def _(Counter, G, pd, plt):
    # Count node type & subtype
    subtype_counts = Counter(
        (attrs.get("type"), attrs.get("sub_type"))
        for _, attrs in G.nodes(data=True)
    )

    # convert to a dataframe
    df_counts = pd.DataFrame(
        [(t, st, count) for (t, st), count in subtype_counts.items()],
        columns=["Node Type", "Subtype", "Count"]
    )

    # change order 
    node_type_order = ["Entity", "Event", "Relationship"]
    df_counts["Node Type"] = pd.Categorical(df_counts["Node Type"], categories=node_type_order, ordered=True)

    # Sort by node type, then subtype
    df_counts = df_counts.sort_values(["Node Type", "Subtype"]).reset_index(drop=True)

    df_counts # show table 


    # we can also visualise this 
    plt.figure(figsize=(18, 5))

    for i, node_type in enumerate(node_type_order, 1): #loop through each node_type
        subset = df_counts[df_counts["Node Type"] == node_type]

        plt.subplot(1, 3, i)
        plt.bar(subset["Subtype"], subset["Count"], color="skyblue")
        plt.title(f"{node_type} Subtype Counts")
        plt.xlabel("Subtype")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")  # rotate subtype labels

    plt.tight_layout()
    plt.show()

    print("Note: y-axis different scale!!, we should consinder this later")
    return


@app.cell
def _(G):
    #check all persons 
    person = [n for n, attrs in G.nodes(data=True) if attrs.get("sub_type") == "Person"]
    print("Persons in the graph (first 10 shown):", person[:10])
    return (person,)


@app.cell
def _(G, nx, person, plt):
    # make function to visualize a person (ego-plot)
    def explore_person(G, person_node): #plot shows network one person, and their communication nodes, and relationships they are connected
        # get neighbours
        neighbours = list(G.neighbors(person_node))
        sub_nodes = [person_node] + neighbours
        subgraph = G.subgraph(sub_nodes)

        # plot ego network
        plt.figure(figsize=(8,6))
        nx.draw(subgraph, with_labels=True, node_size=800)
        plt.title(f"Ego Network for {person_node}")
        plt.show()

        # communication nodes 
        comm_nodes = [n for n in neighbours if G.nodes[n].get("sub_type") == "Communication"]
        print(f"{person_node} is involved in {len(comm_nodes)} message(s):")
        for n in comm_nodes:
            print(n, "-", G.nodes[n].get("content"))

        # Relationship nodes
        rel_nodes = [n for n in neighbours if G.nodes[n].get("type") == "Relationship"]
        print(f"\n{person_node} is part of {len(rel_nodes)} relationship(s):")
        for n in rel_nodes:
            connected_entities = list(G.predecessors(n))
            print(n, "-", connected_entities)

        # returns neighbours 
        return neighbours


    # Explore a person of choice
    person_to_explore = person[0]  # change index to explore a different person
    neighbours = explore_person(G, person_to_explore)
    ##okay this is very annoying because you cannot easily change the person_to_explore in marimo, I think this is usually quite helpful in python. Will look how to fix this in marimo, I think there must be an option 
    return


@app.cell
def _(G, pd):
    # get info colleagues relationship 
    colleagues_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get("sub_type") == "Colleagues"]

    rows = []
    for col_node in colleagues_nodes:
        # persons connected to this relationship
        involved_persons = [n for n in G.predecessors(col_node) if G.nodes[n].get("sub_type") == "Person"]

        # evidence communications nodes
        evidence_msgs = [n for n in G.predecessors(col_node) if G.nodes[n].get("sub_type") == "Communication"]

        rows.append({
            "Colleagues Node": col_node,
            "Persons Involved": ", ".join(involved_persons),
            "Evidence Messages": ", ".join(evidence_msgs),
            "Evidence Count": len(evidence_msgs)
        })

    df_colleagues = pd.DataFrame(rows) #make df from it 

    df_colleagues.head(10) #show dataframe
    return


@app.cell
def _(G):
    #check specific event communication 
    node_id = "Event_Communication_32"

    # Get the node attributes
    communication_attributes = G.nodes[node_id]

    communication_attributes #show attributes nodes (in content you can read the message sent!) - maybe we can do an analysis on the text in future 
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##Make data into dataframe for futher analyis
    """)
    return


@app.cell
def _(G, pd):
    #convert data to dataframe for futher analysis 
    node_df = pd.DataFrame([
        {**attrs, "node_id": n}
        for n, attrs in G.nodes(data=True)
    ])

    edge_df = pd.DataFrame([
        {"source": u, "target": v, **attrs}
        for u, v, attrs in G.edges(data=True)
    ])

    print("node_df shape:", node_df.shape)
    print("edge_df shape:", edge_df.shape)

    node_df.head() # a lot of NA because not all nodes have the same attributes 
    return (node_df,)


@app.cell
def _(node_df):
    # we can also do dataframe per node type? 
    entity_df = node_df[node_df["type"] == "Entity"]#make df for entity 
    entity_df = entity_df.dropna(axis=1, how='all') #drop columns if for entire column NA 

    event_df = node_df[node_df["type"] == "Event"]#make df for event 
    event_df = event_df.dropna(axis=1, how='all') #drop columns if for entire column NA 

    relationship_df = node_df[node_df["type"] == "Relationship"] #make df for relationshp 
    relationship_df = relationship_df.dropna(axis=1, how='all') #drop columns if for entire column NA 

    print("Entities:", entity_df.shape) #check N row & columns
    entity_df.head() #check first few rows 



    return event_df, relationship_df


@app.cell
def _(event_df):

    print("Events:", event_df.shape)#check N row & columns
    event_df.head() # check first few rows

    return


@app.cell
def _(relationship_df):
    print("Relationships:", relationship_df.shape) #check N row & columns
    relationship_df.head() # check first few rows
    return


@app.cell
def _(G, pd):
    from datetime import datetime

    # make a list of communication events, from who to whom and how late
    temporal_list = []

    for timenode in G.nodes():
        # find all communication nodes and find their timestamp
        if G.nodes()[timenode]['sub_type'] == 'Communication':
            time_stamp = datetime.strptime(G.nodes()[timenode]['timestamp'], "%Y-%m-%d %H:%M:%S")

            # find all the senders and receivers of the communication
            com_senders = list(G.predecessors(timenode))
            # also the subtypes of the senders and receivers
            sender_types = [
                G.nodes[sender].get("sub_type")
                for sender in G.predecessors(timenode)
            ]
            com_receivers = list(G.successors(timenode))
            receiver_types = [
                G.nodes[receiver].get("sub_type")
                for receiver in G.successors(timenode)
            ]

            # add info to dataframe
            temporal_list.append({
                "ID": timenode,
                "sender": com_senders,
                "sender_types": sender_types,
                "receiver": com_receivers,
                "receiver_types": receiver_types,
                "hour": time_stamp.hour,
                "content": G.nodes()[timenode]['content']
            })

    temporal_df = pd.DataFrame(temporal_list)
    temporal_df
    return (temporal_df,)


@app.cell
def _(G):
    print(G.predecessors("Sam"))
    return


@app.cell
def _(alt, temporal_df):
    alt.Chart(temporal_df).mark_bar().encode(
        x = alt.X("hour:O"),
        y = alt.Y("count():Q") 
    )
    return


@app.cell
def _(alt, temporal_df):
    temporal_df_exploded = (
        temporal_df
        .explode(["sender", "sender_types"])
    )

    # plot of communications per hour per subtype of entity
    alt.Chart(temporal_df_exploded).mark_line().encode(
        x = alt.X("hour:O"),
        y = alt.Y("count():Q"),
        color = alt.Color("sender_types:N")
    )
    return


@app.cell
def _(G):
    print(G.edges(data = True))

    return


@app.cell
def _(G):
    print(G.nodes(data=True))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
