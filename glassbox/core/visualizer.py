from typing import Optional, Dict

class GraphVisualizer:
    """
    Generates Graphviz DOT source code for the Glass Box engine visualizations.
    Supports: OPro, APE, PromptBreeder, S2A.
    """

    # Boeing/Theme Colors
    COLOR_NODE_DEFAULT = "#1A409F"  # Boeing Blue
    COLOR_NODE_ACTIVE = "#22c55e"   # Green
    COLOR_NODE_TEXT = "white"
    COLOR_EDGE = "#394957"          # Slate Gray
    COLOR_BG = "transparent"

    def _get_node_style(self, node_id: str, active_node_id: Optional[str]) -> str:
        """Returns the DOT attributes for a node, applying active style if matched."""
        fill = self.COLOR_NODE_ACTIVE if node_id == active_node_id else self.COLOR_NODE_DEFAULT
        # Bold border if active
        penwidth = "3" if node_id == active_node_id else "1"
        return f'style="filled,rounded", shape=box, fillcolor="{fill}", fontcolor="{self.COLOR_NODE_TEXT}", fontname="Inter", penwidth={penwidth}'

    def get_opro_dot(self, active_node: Optional[str] = None) -> str:
        """
        Engine A: OPro (Basic Loop)
        Topology: Circular (START -> TEST -> RATE -> CHANGE -> START)
        """
        style_start = self._get_node_style("START", active_node)
        style_test = self._get_node_style("TEST", active_node)
        style_rate = self._get_node_style("RATE", active_node)
        style_change = self._get_node_style("CHANGE", active_node)

        return f"""
        digraph OPro {{
            rankdir=LR;
            bgcolor="{self.COLOR_BG}";
            edge [color="{self.COLOR_EDGE}", penwidth=2];
            
            node [fontsize=12];
            
            # Nodes
            START [label="Current Prompt", {style_start}];
            TEST [label="Test", {style_test}];
            RATE [label="Rate", {style_rate}];
            CHANGE [label="Change", {style_change}];
            
            # Edges (Circular)
            START -> TEST;
            TEST -> RATE;
            RATE -> CHANGE;
            CHANGE -> START;
        }}
        """

    def get_ape_dot(self, active_node: Optional[str] = None) -> str:
        """
        Engine B: APE (Instruction Induction)
        Topology: Circular (Identical structure to OPro, different labels)
        """
        style_start = self._get_node_style("START", active_node)
        style_test = self._get_node_style("TEST", active_node)
        style_rate = self._get_node_style("RATE", active_node)
        style_change = self._get_node_style("CHANGE", active_node)

        return f"""
        digraph APE {{
            rankdir=LR;
            bgcolor="{self.COLOR_BG}";
            edge [color="{self.COLOR_EDGE}", penwidth=2];
            
            node [fontsize=12];
            
            # Nodes
            START [label="Instruction", {style_start}];
            TEST [label="Test", {style_test}];
            RATE [label="Rate", {style_rate}];
            CHANGE [label="Resample", {style_change}];
            
            # Edges
            START -> TEST;
            TEST -> RATE;
            RATE -> CHANGE;
            CHANGE -> START;
        }}
        """

    def get_promptbreeder_dot(self, active_node: Optional[str] = None) -> str:
        """
        Engine C: PromptBreeder (Evolutionary)
        Topology: Figure-8 / Concentric.
        Center: POOL. Inner: TEST, RATE. Outer: MUTATE, CROSS.
        """
        style_pool = self._get_node_style("POOL", active_node)
        style_test = self._get_node_style("TEST", active_node)
        style_rate = self._get_node_style("RATE", active_node)
        style_mutate = self._get_node_style("MUTATE", active_node)
        style_cross = self._get_node_style("CROSS", active_node)

        return f"""
        digraph PromptBreeder {{
            rankdir=LR;
            bgcolor="{self.COLOR_BG}";
            edge [color="{self.COLOR_EDGE}", penwidth=2];
            
            node [fontsize=12];
            
            # Nodes
            POOL [label="Population", {style_pool}, shape=octagon];
            TEST [label="Test", {style_test}];
            RATE [label="Rate", {style_rate}];
            MUTATE [label="Mutate", {style_mutate}];
            CROSS [label="Cross", {style_cross}];
            
            # Inner Loop (Evaluation)
            POOL -> TEST [weight=2];
            TEST -> RATE [weight=2];
            RATE -> POOL [weight=2];
            
            # Outer Loop (Evolution)
            POOL -> MUTATE [style=dashed];
            MUTATE -> CROSS [style=dashed];
            CROSS -> POOL [style=dashed];
        }}
        """

    def get_s2a_dot(self, active_node: Optional[str] = None) -> str:
        """
        Engine D: S2A (System 2 Attention)
        Topology: Linear Pipeline (READ -> FILTER -> REFINE -> ANSWER)
        """
        style_read = self._get_node_style("READ", active_node)
        style_filter = self._get_node_style("FILTER", active_node)
        style_refine = self._get_node_style("REFINE", active_node)
        style_answer = self._get_node_style("ANSWER", active_node)

        return f"""
        digraph S2A {{
            rankdir=LR;
            bgcolor="{self.COLOR_BG}";
            edge [color="{self.COLOR_EDGE}", penwidth=2];
            
            node [fontsize=12];
            
            # Nodes
            READ [label="Read Context", {style_read}];
            FILTER [label="Filter", {style_filter}];
            REFINE [label="Refine", {style_refine}];
            ANSWER [label="Answer", {style_answer}, shape=doubleoctagon];
            
            # Edges
            READ -> FILTER;
            FILTER -> REFINE;
            REFINE -> ANSWER;
        }}
        """

    def get_engine_chart(self, engine_id: str, active_node: Optional[str] = None) -> str:
        """Factory method to get the correct chart source."""
        if engine_id == "opro":
            return self.get_opro_dot(active_node)
        elif engine_id == "ape":
            return self.get_ape_dot(active_node)
        elif engine_id == "promptbreeder":
            return self.get_promptbreeder_dot(active_node)
        elif engine_id == "s2a":
            return self.get_s2a_dot(active_node)
        else:
            return self.get_opro_dot(active_node)  # Default
