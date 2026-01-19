"""
Zone F: Export Panel - PDF Report and Export Options

Provides export functionality for optimization sessions.
"""

import streamlit as st
from typing import Optional

from glassbox.models.session import OptimizerSession
from glassbox.utils.export import (
    generate_pdf_report,
    export_session_json,
    export_trajectory_csv,
    export_candidates_csv
)


def render_export_panel(session: Optional[OptimizerSession] = None):
    """Render the export options panel."""
    
    with st.expander("📄 Export Options", expanded=False):
        if not session or not session.candidates:
            st.info("Complete an optimization run to enable exports.")
            return
        
        st.markdown("**Export your optimization results**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # PDF Report
            st.markdown("##### 📊 PDF Report")
            if st.button("Generate PDF", key="gen_pdf", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    try:
                        pdf_bytes = generate_pdf_report(session)
                        st.download_button(
                            "⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=f"glassbox_report_{session.metadata.session_id[:8]}.pdf",
                            mime="application/pdf",
                            key="download_pdf"
                        )
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")
            
            # Session JSON
            st.markdown("##### 💾 Session File (.opro)")
            json_data = export_session_json(session)
            st.download_button(
                "⬇️ Download .opro",
                data=json_data,
                file_name=f"session_{session.metadata.session_id[:8]}.opro",
                mime="application/json",
                key="download_opro"
            )
        
        with col2:
            # CSV Exports
            st.markdown("##### 📈 Trajectory CSV")
            traj_csv = export_trajectory_csv(session)
            st.download_button(
                "⬇️ Download Trajectory",
                data=traj_csv,
                file_name="trajectory.csv",
                mime="text/csv",
                key="download_traj_csv"
            )
            
            st.markdown("##### 🏆 Candidates CSV")
            cand_csv = export_candidates_csv(session)
            st.download_button(
                "⬇️ Download Candidates",
                data=cand_csv,
                file_name="candidates.csv",
                mime="text/csv",
                key="download_cand_csv"
            )
        
        # Quick stats
        st.markdown("---")
        st.markdown("**Session Summary**")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Total Steps", len(session.trajectory))
        with col_b:
            st.metric("Total Candidates", len(session.candidates))
        with col_c:
            best = session.get_best_candidate()
            st.metric("Best Score", f"{best.global_score:.1f}" if best else "—")
        with col_d:
            st.metric("Engine", session.metadata.engine_used[:10])
