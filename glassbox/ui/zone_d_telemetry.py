"""
Zone D: Telemetry Graph - Top Right

Contains:
- Live updating score graph (Plotly)
- Average and Max score lines
- Star markers for new high scores
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List

from glassbox.models.session import TrajectoryEntry


def render_zone_d(trajectory: List[TrajectoryEntry]):
    """Render the telemetry graph zone."""
    
    st.markdown("### 📈 Optimization Progress")
    
    if not trajectory:
        # Placeholder chart
        fig = _create_placeholder_chart()
        st.plotly_chart(fig, use_container_width=True, key="telemetry_placeholder")
        st.caption("Graph will populate as optimization progresses...")
        return

    # Extract data
    steps = [entry.step for entry in trajectory]
    scores = [entry.score for entry in trajectory]
    
    # Calculate running average and max
    avg_scores = []
    max_scores = []
    running_max = 0
    
    for i, score in enumerate(scores):
        avg_scores.append(sum(scores[:i+1]) / (i+1))
        running_max = max(running_max, score)
        max_scores.append(running_max)

    # Find new high score points (for star markers)
    star_steps = []
    star_scores = []
    current_max = 0
    for step, score in zip(steps, scores):
        if score > current_max:
            current_max = score
            star_steps.append(step)
            star_scores.append(score)

    # Create figure
    fig = go.Figure()

    # Average score line (solid blue)
    fig.add_trace(go.Scatter(
        x=steps,
        y=avg_scores,
        mode='lines',
        name='Average Score',
        line=dict(color='#3B82F6', width=2),
        hovertemplate='Step %{x}<br>Avg: %{y:.1f}<extra></extra>'
    ))

    # Max score line (dashed green)
    fig.add_trace(go.Scatter(
        x=steps,
        y=max_scores,
        mode='lines',
        name='Max Score',
        line=dict(color='#22c55e', width=2, dash='dash'),
        hovertemplate='Step %{x}<br>Max: %{y:.1f}<extra></extra>'
    ))

    # Star markers for new highs
    fig.add_trace(go.Scatter(
        x=star_steps,
        y=star_scores,
        mode='markers',
        name='New High!',
        marker=dict(
            symbol='star',
            size=15,
            color='#FFD700',
            line=dict(color='#FFA500', width=2)
        ),
        hovertemplate='🌟 New High!<br>Step %{x}<br>Score: %{y:.1f}<extra></extra>'
    ))

    # Layout
    fig.update_layout(
        xaxis_title='Step',
        yaxis_title='Score (0-100)',
        yaxis=dict(range=[0, 105]),
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='#FAFAFA'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=40, r=20, t=40, b=40),
        hovermode='x unified'
    )

    # Grid styling
    fig.update_xaxes(gridcolor='#31333F', zeroline=False)
    fig.update_yaxes(gridcolor='#31333F', zeroline=False)

    # Render
    st.plotly_chart(fig, use_container_width=True, key="telemetry_chart")

    # Stats summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current", f"{scores[-1]:.1f}" if scores else "—")
    
    with col2:
        st.metric("Average", f"{avg_scores[-1]:.1f}" if avg_scores else "—")
    
    with col3:
        st.metric("Best", f"{max(scores):.1f}" if scores else "—")
    
    with col4:
        if len(scores) >= 2:
            delta = scores[-1] - scores[-2]
            st.metric("Δ Last", f"{delta:+.1f}")
        else:
            st.metric("Δ Last", "—")


def _create_placeholder_chart():
    """Create a placeholder chart before optimization starts."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[0, 1, 2, 3],
        y=[0, 0, 0, 0],
        mode='lines',
        line=dict(color='#31333F', width=1, dash='dot'),
        showlegend=False
    ))

    fig.update_layout(
        xaxis_title='Step',
        yaxis_title='Score (0-100)',
        yaxis=dict(range=[0, 105]),
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='#666666'),
        margin=dict(l=40, r=20, t=20, b=40),
        annotations=[
            dict(
                text="Waiting for data...",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="#666666")
            )
        ]
    )

    fig.update_xaxes(gridcolor='#31333F', zeroline=False)
    fig.update_yaxes(gridcolor='#31333F', zeroline=False)
    
    return fig


def render_mini_telemetry(trajectory: List[TrajectoryEntry]):
    """Render a compact sparkline version of the telemetry."""
    if not trajectory:
        st.caption("📊 —")
        return

    scores = [entry.score for entry in trajectory[-10:]]  # Last 10 points
    
    # Simple sparkline using plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=scores,
        mode='lines',
        line=dict(color='#20C20E', width=2),
        fill='tozeroy',
        fillcolor='rgba(32, 194, 14, 0.2)'
    ))
    
    fig.update_layout(
        height=60,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, range=[0, 105]),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True, key="mini_telemetry")
