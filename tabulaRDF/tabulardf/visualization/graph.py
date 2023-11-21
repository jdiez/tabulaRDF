import kglab


def create_graph(rdf_file: str, vis_style: dict, out_file: str) -> str:
    """
    """
    kg = kglab.KnowledgeGraph().load_rdf(rdf_file)  #("tmp.ttl")
    subgraph = kglab.SubgraphTensor(kg)
    pyvis_graph = subgraph.build_pyvis_graph(notebook=True, style=vis_style)
    pyvis_graph.force_atlas_2based()
    pyvis_graph.show(out_file)    #("tmp.fig03.html")


def main():
    pass


if __name__ == '__main__':
    pass

