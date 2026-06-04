from graphs.smartplots_graph import smartplots_graph

result = smartplots_graph.invoke(
    {
        "query": "Austin land under 100k for camping",
        "filters": {},
        "plots": [],
        "ranked_plots": [],
        "response": "",
    }
)

print(result["response"])