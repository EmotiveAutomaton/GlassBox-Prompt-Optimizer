"""
Export Utilities - PDF Report Generation and Session Export

Creates professional PDF reports from optimization sessions.
"""

import io
import json
from datetime import datetime
from typing import Optional, List
from dataclasses import asdict

from glassbox.models.session import OptimizerSession
from glassbox.models.candidate import UnifiedCandidate


def generate_pdf_report(session: OptimizerSession) -> bytes:
    """
    Generate a PDF report from optimization session.
    
    Requires: reportlab or fallback to HTML-based PDF
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        return _generate_reportlab_pdf(session)
    except ImportError:
        # Fallback to simple text-based PDF
        return _generate_simple_pdf(session)


def _generate_reportlab_pdf(session: OptimizerSession) -> bytes:
    """Generate PDF using ReportLab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#20C20E'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#20C20E'),
        spaceBefore=15,
        spaceAfter=10
    )
    body_style = styles['BodyText']
    
    elements = []
    
    # Title
    elements.append(Paragraph("GlassBox Prompt Optimization Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Metadata
    meta_data = [
        ["Session ID", session.metadata.session_id[:16] + "..."],
        ["Engine Used", session.metadata.engine_used],
        ["Timestamp", session.metadata.timestamp[:19]],
        ["Model", session.config.model],
        ["Temperature", str(session.config.temperature)],
    ]
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#31333F')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))
    
    # Seed Prompt
    elements.append(Paragraph("Seed Prompt", heading_style))
    elements.append(Paragraph(session.seed_prompt or "N/A", body_style))
    elements.append(Spacer(1, 15))
    
    # Winner
    if session.winner:
        elements.append(Paragraph("Winning Prompt", heading_style))
        elements.append(Paragraph(f"Score: {session.winner.score_aggregate:.1f}/100", body_style))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(session.winner.full_content, body_style))
        elements.append(Spacer(1, 15))
    
    # Trajectory Summary
    if session.trajectory:
        elements.append(Paragraph("Optimization History", heading_style))
        traj_data = [["Step", "Score", "Prompt Preview"]]
        for entry in session.trajectory[-10:]:  # Last 10
            preview = entry.prompt[:40] + "..." if len(entry.prompt) > 40 else entry.prompt
            traj_data.append([str(entry.step), f"{entry.score:.1f}", preview])
        
        traj_table = Table(traj_data, colWidths=[0.75*inch, 0.75*inch, 4.5*inch])
        traj_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#20C20E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#31333F')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#0E1117')),
        ]))
        elements.append(traj_table)
        elements.append(Spacer(1, 15))
    
    # Top Candidates
    if session.candidates:
        elements.append(Paragraph("Top Candidates", heading_style))
        sorted_candidates = sorted(session.candidates, key=lambda c: c.score_aggregate, reverse=True)
        
        for i, candidate in enumerate(sorted_candidates[:5]):
            results = candidate.test_results
            score_a = results.get("input_a", 0)
            score_b = results.get("input_b", 0)
            score_c = results.get("input_c", 0)
            
            elements.append(Paragraph(
                f"#{i+1} - Score: {candidate.score_aggregate:.1f} | "
                f"Traffic: ({'✓' if score_a >= 50 else '✗'}"
                f"{'✓' if score_b >= 50 else '✗'}"
                f"{'✓' if score_c >= 50 else '✗'})",
                body_style
            ))
            elements.append(Paragraph(
                candidate.display_text[:200] + "..." if len(candidate.display_text) > 200 else candidate.display_text,
                body_style
            ))
            elements.append(Spacer(1, 8))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def _generate_simple_pdf(session: OptimizerSession) -> bytes:
    """Generate simple text-based PDF without ReportLab."""
    # Create a simple text file as fallback
    lines = [
        "=" * 60,
        "GLASSBOX PROMPT OPTIMIZATION REPORT",
        "=" * 60,
        "",
        f"Session ID: {session.metadata.session_id}",
        f"Engine: {session.metadata.engine_used}",
        f"Timestamp: {session.metadata.timestamp}",
        f"Model: {session.config.model}",
        "",
        "-" * 40,
        "SEED PROMPT:",
        "-" * 40,
        session.seed_prompt or "N/A",
        "",
    ]
    
    if session.winner:
        lines.extend([
            "-" * 40,
            f"WINNING PROMPT (Score: {session.winner.score_aggregate:.1f}):",
            "-" * 40,
            session.winner.full_content,
            "",
        ])
    
    if session.trajectory:
        lines.extend([
            "-" * 40,
            "OPTIMIZATION HISTORY:",
            "-" * 40,
        ])
        for entry in session.trajectory:
            lines.append(f"Step {entry.step}: {entry.score:.1f} - {entry.prompt[:50]}...")
    
    return "\n".join(lines).encode('utf-8')


def export_session_json(session: OptimizerSession, pretty: bool = True) -> str:
    """Export session to JSON string."""
    return session.to_json(indent=2 if pretty else None)


def export_trajectory_csv(session: OptimizerSession) -> str:
    """Export trajectory to CSV format."""
    lines = ["step,score,prompt"]
    for entry in session.trajectory:
        # Escape quotes in prompt
        prompt_escaped = entry.prompt.replace('"', '""')
        lines.append(f'{entry.step},{entry.score:.2f},"{prompt_escaped}"')
    return "\n".join(lines)


def export_candidates_csv(session: OptimizerSession) -> str:
    """Export all candidates to CSV format."""
    lines = ["id,global_score,score_a,score_b,score_c,generation,prompt"]
    for c in session.candidates:
        prompt_escaped = c.display_text.replace('"', '""')
        results = c.test_results
        score_a = results.get("input_a", 0)
        score_b = results.get("input_b", 0)
        score_c = results.get("input_c", 0)
        
        lines.append(
            f'{c.id},{c.score_aggregate:.2f},{score_a:.2f},{score_b:.2f},'
            f'{score_c:.2f},{c.generation_index},"{prompt_escaped}"'
        )
    return "\n".join(lines)
