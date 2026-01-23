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
    COLOR_BRIDGE_PROMPT = "#3b82f6" # Blue for Prompt Bridge
    COLOR_BRIDGE_DATA = "#eab308"   # Yellow for Data Bridge

    def _get_node_style(self, node_id: str, active_node_id: Optional[str], pos: str) -> str:
        """Returns the DOT attributes for a node, applying active style if matched and Fixed Position."""
        fill = self.COLOR_NODE_ACTIVE if node_id == active_node_id else self.COLOR_NODE_DEFAULT
        # Bold border if active
        penwidth = "3" if node_id == active_node_id else "1"
        return f'style="filled,rounded", shape=box, fillcolor="{fill}", fontcolor="{self.COLOR_NODE_TEXT}", fontname="Inter", penwidth={penwidth}, pos="{pos}!"'

    def _get_common_graph_setup(self) -> str:
        """Returns common graph attributes for neato engine."""
        return f"""
            layout=neato;
            bgcolor="{self.COLOR_BG}";
            splines=curved;
            edge [color="{self.COLOR_EDGE}", penwidth=2, arrowsize=0.8];
            node [fontsize=11];
        """

    def _add_bridging_logic(self, dot_lines: list, cycle_count: int, start_node: str):
        """Adds the Input UI Bridging (Blue) and Persistent Data (Yellow) edges."""
        # 1. UI Anchors (Invisible nodes positioned to the left)
        dot_lines.append(f'UI_INPUT [label="", style=invis, pos="-5,0!"];')
        dot_lines.append(f'UI_DATA [label="", style=invis, pos="-5,1!"];')

        # 2. Cycle 0: Blue Edge (UI -> Start)
        if cycle_count == 0:
            dot_lines.append(f'UI_INPUT -> {start_node} [color="{self.COLOR_BRIDGE_PROMPT}", style=dashed, label="Init"];')
        
        # 3. All Cycles: Yellow Edge (Data -> Test/Persistent)
        # We assume 'TEST' is the data ingestion point usually, or we pass it in.
        # For simplicity, we'll handle the specific edge connection in the engine method if it differs,
        # but here we provide the anchor.
        pass 

    def get_opro_dot(self, active_node: Optional[str] = None, cycle_count: int = 0) -> str:
        """
        Engine A: OPro (Iterative Oval)
        Positions: Oval shape.
        """
        # Coordinates (Normalized 4x2 grid)
        p_start, p_test, p_rate, p_change = "-2,0", "0,1", "2,0", "0,-1"
        
        style_start = self._get_node_style("START", active_node, p_start)
        style_test = self._get_node_style("TEST", active_node, p_test)
        style_rate = self._get_node_style("RATE", active_node, p_rate)
        style_change = self._get_node_style("CHANGE", active_node, p_change)

        lines = [
            f"digraph OPro {{",
            self._get_common_graph_setup(),
            
            # Nodes
            f'START [label="Current Prompt", {style_start}];',
            f'TEST [label="Test", {style_test}];',
            f'RATE [label="Rate", {style_rate}];',
            f'CHANGE [label="Change", {style_change}];'
        ]

        # Bridging
        self._add_bridging_logic(lines, cycle_count, "START")
        # Persistent Data -> TEST
        lines.append(f'UI_DATA -> TEST [color="{self.COLOR_BRIDGE_DATA}", penwidth=2.0];')

        # Edges (Circular)
        lines.extend([
            "START -> TEST;",
            "TEST -> RATE;",
            "RATE -> CHANGE;",
            "CHANGE -> START;"
        ])
        
        lines.append("}")
        return "\n".join(lines)

    def get_ape_dot(self, active_node: Optional[str] = None, cycle_count: int = 0) -> str:
        """
        Engine B: APE (Reverse Eng Oval)
        Same layout as OPro, different labels.
        """
        p_start, p_test, p_rate, p_change = "-2,0", "0,1", "2,0", "0,-1"
        
        style_start = self._get_node_style("START", active_node, p_start)
        style_test = self._get_node_style("TEST", active_node, p_test)
        style_rate = self._get_node_style("RATE", active_node, p_rate)
        style_change = self._get_node_style("CHANGE", active_node, p_change)

        lines = [
            f"digraph APE {{",
            self._get_common_graph_setup(),
            
            # Nodes
            f'START [label="Instruction", {style_start}];',
            f'TEST [label="Test", {style_test}];',
            f'RATE [label="Rate", {style_rate}];',
            f'CHANGE [label="Resample", {style_change}];'
        ]
        
        # Bridging
        self._add_bridging_logic(lines, cycle_count, "START")
        # Persistent Data -> INSTRUCT (Induction) & TEST (Validation)
        lines.append(f'UI_DATA -> START [color="{self.COLOR_BRIDGE_DATA}", penwidth=2.0];') 
        lines.append(f'UI_DATA -> TEST [color="{self.COLOR_BRIDGE_DATA}", penwidth=2.0];')

        # Edges
        lines.extend([
            "START -> TEST;",
            "TEST -> RATE;",
            "RATE -> CHANGE;",
            "CHANGE -> START;"
        ])
        
        lines.append("}")
        return "\n".join(lines)

    def get_promptbreeder_dot(self, active_node: Optional[str] = None, cycle_count: int = 0) -> str:
        """
        Engine C: PromptBreeder (Figure-8)
        Inner Loop (Execution): POOL -> TEST -> RATE -> POOL
        Outer Loop (Evolution): POOL -> MUTATE -> CROSS -> POOL
        """
        # Positions
        p_pool = "-1,0"
        p_test = "0,1"
        p_rate = "1,0"
        p_mutate = "-1,-1.5" # Bottom Leftish
        p_cross  = "1,-1.5"  # Bottom Rightish

        style_pool = self._get_node_style("POOL", active_node, p_pool)
        style_test = self._get_node_style("TEST", active_node, p_test)
        style_rate = self._get_node_style("RATE", active_node, p_rate)
        style_mutate = self._get_node_style("MUTATE", active_node, p_mutate)
        style_cross = self._get_node_style("CROSS", active_node, p_cross)

        lines = [
            f"digraph PromptBreeder {{",
            self._get_common_graph_setup(),
            
            # Nodes
            f'POOL [label="Population", {style_pool}, shape=octagon];',
            f'TEST [label="Test", {style_test}];',
            f'RATE [label="Rate", {style_rate}];',
            f'MUTATE [label="Mutate", {style_mutate}];',
            f'CROSS [label="Cross", {style_cross}];'
        ]

        # Bridging
        self._add_bridging_logic(lines, cycle_count, "POOL")
        # Persistent Data -> TEST
        lines.append(f'UI_DATA -> TEST [color="{self.COLOR_BRIDGE_DATA}", penwidth=2.0];')

        # Inner Loop (Execution) - Solid
        lines.extend([
            "POOL -> TEST [weight=2];",
            "TEST -> RATE [weight=2];",
            "RATE -> POOL [weight=2];"
        ])
        
        # Outer Loop (Evolution) - Dashed
        lines.extend([
            "POOL -> MUTATE [style=dashed];",
            "MUTATE -> CROSS [style=dashed];",
            "CROSS -> POOL [style=dashed];"
        ])
        
        lines.append("}")
        return "\n".join(lines)

    def get_s2a_dot(self, active_node: Optional[str] = None, cycle_count: int = 0) -> str:
        """
        Engine D: S2A (Optimization Wrapper)
        Oval: FILTER -> TEST_BENCH -> EVALUATE -> OPTIMIZE -> FILTER
        """
        # Positions
        p_filter = "-2,0"
        p_test = "0,1"
        p_eval = "2,0"
        p_opt = "0,-1"

        style_filter = self._get_node_style("FILTER", active_node, p_filter)
        style_test = self._get_node_style("TEST_BENCH", active_node, p_test)
        style_eval = self._get_node_style("EVALUATE", active_node, p_eval)
        style_opt = self._get_node_style("OPTIMIZE", active_node, p_opt)
        
        # Internal Runtime nodes (Invisible/Implicit or Subgraph? Spec says "This node conceptually contains...")
        # We will just stick to the main Optimization Loop nodes for now as per "Visual Topology" 5.4.1

        lines = [
            f"digraph S2A {{",
            self._get_common_graph_setup(),
            
            # Nodes
            f'FILTER [label="Filter Prompt", {style_filter}];',
            f'TEST_BENCH [label="Test Bench", {style_test}, shape=doubleoctagon];',
            f'EVALUATE [label="Evaluate", {style_eval}];',
            f'OPTIMIZE [label="Optimize", {style_opt}];'
        ]

        # Bridging
        self._add_bridging_logic(lines, cycle_count, "FILTER")
        # Data -> Test Bench
        lines.append(f'UI_DATA -> TEST_BENCH [color="{self.COLOR_BRIDGE_DATA}", penwidth=2.0];')

        # Edges
        lines.extend([
            "FILTER -> TEST_BENCH;",
            "TEST_BENCH -> EVALUATE;",
            "EVALUATE -> OPTIMIZE;",
            "OPTIMIZE -> FILTER;"
        ])
        
        lines.append("}")
        return "\n".join(lines)

    def get_engine_chart(self, engine_id: str, active_node: Optional[str] = None, cycle_count: int = 0) -> str:
        """Factory method to get the correct chart source."""
        if engine_id == "opro":
            return self.get_opro_dot(active_node, cycle_count)
        elif engine_id == "ape":
            return self.get_ape_dot(active_node, cycle_count)
        elif engine_id == "promptbreeder":
            return self.get_promptbreeder_dot(active_node, cycle_count)
        elif engine_id == "s2a":
            return self.get_s2a_dot(active_node, cycle_count)
        else:
            return self.get_opro_dot(active_node, cycle_count)
