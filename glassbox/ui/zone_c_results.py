"""
Zone C: Results & Candidate Management
Restructured into Card Boxes:
- Card: "POTENTIAL PROMPTS" (left, full height)
- Card: "PROMPT RATINGS" (right top - graph)
- Card: "FINAL OUTPUT AND USER EVALUATION" (right bottom)
"""

import streamlit as st
from typing import List, Optional
import difflib

from glassbox.models.session import CandidateResult


def render_zone_c(candidates: List[CandidateResult], selected_ids: List[str] = None):
    """Render the results zone with card box layout."""
    
    # --- THREE CARDS: Left Column (POTENTIAL PROMPTS) | Right Column (RATINGS + FINAL OUTPUT) ---
    col_prompts, col_right = st.columns([1, 1.5])
    
    # === CARD: POTENTIAL PROMPTS ===
    with col_prompts:
        st.markdown('''
            <div class="boeing-card" style="height: 100%;">
                <div class="boeing-card-header">POTENTIAL PROMPTS</div>
                <div class="boeing-card-content">
        ''', unsafe_allow_html=True)
        
        if not candidates:
            st.info("No candidates yet. Start optimization to generate prompt variations.")
        else:
            sorted_candidates = sorted(candidates, key=lambda c: c.global_score, reverse=True)
            
            for i, candidate in enumerate(sorted_candidates[:10]):
                score = candidate.global_score
                color = "#22c55e" if score >= 80 else "#eab308" if score >= 50 else "#ef4444"
                preview = candidate.prompt_text[:50] + "..." if len(candidate.prompt_text) > 50 else candidate.prompt_text
                
                col_rank, col_main = st.columns([0.3, 2])
                with col_rank:
                    st.markdown(f"<span style='color:{color};font-weight:bold;'>{score:.0f}</span>", unsafe_allow_html=True)
                with col_main:
                    if st.button(preview, key=f"select_{candidate.id}", use_container_width=True):
                        st.session_state["selected_candidate"] = candidate.id
                
                if i < len(sorted_candidates) - 1:
                    st.markdown("<hr style='margin:2px 0;border-color:#E0E0E0;'>", unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # === RIGHT COLUMN: RATINGS + FINAL OUTPUT ===
    with col_right:
        # === CARD: PROMPT RATINGS (Graph) ===
        st.markdown('''
            <div class="boeing-card">
                <div class="boeing-card-header">PROMPT RATINGS</div>
                <div class="boeing-card-content">
        ''', unsafe_allow_html=True)
        
        if candidates:
            # Simple bar chart of top candidates
            import pandas as pd
            top_5 = sorted(candidates, key=lambda c: c.global_score, reverse=True)[:5]
            chart_data = pd.DataFrame({
                "Candidate": [f"#{i+1}" for i in range(len(top_5))],
                "Score": [c.global_score for c in top_5]
            })
            st.bar_chart(chart_data.set_index("Candidate"), height=200)
        else:
            st.markdown("<div style='height:150px;display:flex;align-items:center;justify-content:center;color:#999;'>No data yet</div>", unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # === CARD: FINAL OUTPUT AND USER EVALUATION ===
        st.markdown('''
            <div class="boeing-card">
                <div class="boeing-card-header">FINAL OUTPUT AND USER EVALUATION</div>
                <div class="boeing-card-content">
        ''', unsafe_allow_html=True)
        
        selected_id = st.session_state.get("selected_candidate")
        if selected_id and candidates:
            candidate = next((c for c in candidates if c.id == selected_id), None)
            if candidate:
                st.code(candidate.prompt_text, language="text")
                
                col_score, col_actions = st.columns([1, 2])
                with col_score:
                    st.metric("Final Score", f"{candidate.global_score:.1f}")
                with col_actions:
                    new_score = st.number_input("Override Score", 0.0, 100.0, 
                                                candidate.global_score, 5.0,
                                                key="final_override", label_visibility="collapsed")
                    if st.button("Apply & Accept", type="primary", use_container_width=True):
                        candidate.human_override_score = new_score
                        st.success("Prompt accepted!")
        else:
            st.markdown("<div style='padding:20px;color:#666;text-align:center;'>Select a prompt from POTENTIAL PROMPTS to evaluate</div>", unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)


def render_zone_d_inline():
    """Inline graph rendering for PROMPT RATINGS card - placeholder for Zone D integration."""
    pass
