# Visual Tether Strategies: Zone D Graph to Zone E Details

**Objective:** Connect the Primary Selection point in the Optimization Graph (Zone D) to the Header of the Prompt Inspector (Zone E) to visually reinforce that Zone E dictates the detail of the selected point.

**Constraint:** Zone D and Zone E are separate Streamlit containers (often separate CSS stacking contexts), making direct SVG/Canvas connectors difficult without custom React components or hacky overlays.

## Strategy 1: The "Left Rail" Circuit (User Suggestion)
**Concept:**
Instead of dropping straight down, the dashed line extends horizontally to the **Left**, exits the graph area, travels down the "gutter" or sidebar area, and hooks into the left side of Zone E.

**Pros:**
*   Avoids crossing over other data points or the X-axis labels.
*   Clearly circuit-like, implying a "wiring" connection.

**Implementation Plan:**
1.  **Graph Shapes (Plotly):**
    *   Line 1: `(x_point, y_point) -> (x_min - margin, y_point)` [Horizontal Left]
    *   Line 2: `(x_min - margin, y_point) -> (x_min - margin, y_bottom)` [Vertical Down]
2.  **CSS/HTML Bridge:** 
    *   This is the hard part. The graph stops at its container edge.
    *   We would need to render the "Vertical Down" portion *outside* the graph, or push the graph margin so far left that it encompasses the rail.
    *   *Viable Approach:* Use a Plotly Shape for the entire path, but set `xref='paper'` and `x=-0.X` (negative coordinates) to draw in the left margin of the plot.

## Strategy 2: The "Container Flush" Drop (Current Implementation)
**Concept:**
A vertical dashed line drops from `(x_point, y_point)` straight down to the absolute bottom of the graph container (`yref='paper', y0=0`).
Zone E's Header is styled to hug the top of its container, minimizing the gap.

**Pros:**
*   Simple to implement in Plotly.
*   Robust against window resizing.

**Cons:**
*   There is still a "White Gap" between the Graph Card and the Details Card (standard Streamlit padding).

## Strategy 3: The "Chevron" Header
**Concept:**
Zone E's Header includes a visual "Pointer" or Chevron that moves horizontally to match the X-position of the selected point above it.

**Implementation:**
*   Pass `generation_index` to Zone E.
*   Calculate `left: {percent}%` for a pseudo-element arrow on the header.
*   *Difficulty:* Mapping "Iteration Index" to "CSS Percentage" accurately is tricky with responsive resizing.

## Recommendation
**Strategy 1 (Left Rail)** is the most visually distinct and "premium" feel, matching the "GlassBox" circuit aesthetic.
*   **Next Step:** Experiment with negative `xref` in Plotly to see if we can draw a "Left Hook" shape that extends past the Y-axis.
