# -*- coding: utf-8 -*-
"""
====
QIR Function visualization
====

Uses python plotting tools to visualize the blocks in a `QirFunction`.
"""

import pyqir_parser as pqp
import matplotlib.pyplot as plt
import networkx as nx
from pyvis import network as net

# Need a way of telling if a block has quantum instructions.
# This is probably wrong as written rn, may want to filter further.
def is_block_quantum(block : pqp.QirBlock) -> bool:
    return any(
        isinstance(instruction, pqp.QirQisCallInstr) 
        for instruction in block.instructions
    )

# Adds metadata as a dict to a node derived from a block's contents.
def qir_block_style(block : pqp.QirBlock) -> dict:
    return {
        "node_color" : "red" if is_block_quantum(block) else "blue",
        "node_name" : block.name,
        "is_endpoint" : block.name == 'entry'
    }

# Pyvis expects node labels to be strings, so this just makes a new copy
# of a graph and replaces the nodes keyed with `QirBlock` to the 
# name property of the block
def graph_to_pyvis(graph : "nx.MultiDiGraph") -> "nx.MultiDiGraph":
    new_graph = graph.copy()
    mapping = {block: data["node_name"] for block, data in new_graph.nodes(data=True)}
    return nx.relabel_nodes(new_graph, mapping)

#get a dict of edges : edge label simplified by truncation
def graph_edge_labels_simple(graph : "nx.MultiDiGraph") -> dict:
    return {(e1, e2): data["cond"] for e1, e2, data in graph.edges(data=True)}

# Generates a NetworkX graph corrisponding to the blocks in 
# PyQIR function.
def control_flow_graph_netx(func : pqp.QirFunction) -> "nx.MultiDiGraph":
    cfg = nx.MultiDiGraph()
    blocks_by_name = {} 
    for block in func.blocks:
        cfg.add_node(block, **qir_block_style(block))
        blocks_by_name[block.name] = block
    
    return_node = "return"
    bottom_node = None
    
    cfg.add_node(return_node, **{
        "node_color" : "blue",
        "node_name" : return_node,
        "is_endpoint" : True
    })

    for block in blocks_by_name.values():
        term = block.terminator
        if isinstance(term, pqp.QirCondBrTerminator):
            cfg.add_edge(block, blocks_by_name[term.true_dest], cond="True")
            cfg.add_edge(block, blocks_by_name[term.false_dest], cond="False")
        elif isinstance(term, pqp.QirBrTerminator):
            cfg.add_edge(block, blocks_by_name[term.dest], cond="()")
        elif isinstance(term, pqp.QirRetTerminator):
            cfg.add_edge(block, return_node, cond="()")
        elif isinstance(term, pqp.QirSwitchTerminator):
            print(f"Not yet implemented: {term} in {block}")
        elif isinstance(term, pqp.QirUnreachableTerminator):
            if bottom_node is None:
                bottom_node = "⊥"
            cfg.add_edge(block, bottom_node)
        else:
            print(f"Not yet implemented: {term} in {block}")

    return cfg
    