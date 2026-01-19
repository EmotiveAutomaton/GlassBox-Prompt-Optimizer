"""
Utility Functions - Threading, Diff Engine, and Helpers

Includes:
- Thread-safe utilities per Boeing spec 2.3
- HTML diff generation
- General helpers
"""

import threading
import queue
import difflib
from typing import Any, Callable, Optional, List
from dataclasses import dataclass
import html


@dataclass
class ThreadResult:
    """Result container for background tasks."""
    success: bool
    data: Any = None
    error: str = ""


class StoppableThread(threading.Thread):
    """
    Thread with stop signal support per Boeing spec 2.3.
    
    Usage:
        def worker(stop_event):
            while not stop_event.is_set():
                # do work
                pass
        
        thread = StoppableThread(target=worker)
        thread.start()
        thread.request_stop()
    """

    def __init__(self, target: Callable, *args, **kwargs):
        self._stop_event = threading.Event()
        
        # Wrap target to pass stop event
        def wrapped_target(*a, **kw):
            return target(self._stop_event, *a, **kw)
        
        super().__init__(target=wrapped_target, daemon=True, *args, **kwargs)
        self.result_queue = queue.Queue()

    def request_stop(self):
        """Signal thread to stop."""
        self._stop_event.set()

    def is_stop_requested(self) -> bool:
        """Check if stop was requested."""
        return self._stop_event.is_set()

    def get_result(self, timeout: float = None) -> Optional[ThreadResult]:
        """Get result from queue with optional timeout."""
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None


class TaskQueue:
    """
    Thread-safe task queue for optimization steps.
    
    Allows UI to check progress without blocking.
    """

    def __init__(self, maxsize: int = 100):
        self._queue = queue.Queue(maxsize=maxsize)
        self._results = []
        self._lock = threading.Lock()

    def put(self, item: Any):
        """Add item to queue."""
        self._queue.put(item)

    def get(self, timeout: float = 0.1) -> Optional[Any]:
        """Get item from queue with timeout."""
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_all(self) -> List[Any]:
        """Get all items without blocking."""
        items = []
        while True:
            try:
                items.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return items

    def store_result(self, result: Any):
        """Store a result for later retrieval."""
        with self._lock:
            self._results.append(result)

    def get_results(self) -> List[Any]:
        """Get all stored results."""
        with self._lock:
            return list(self._results)

    def clear_results(self):
        """Clear stored results."""
        with self._lock:
            self._results.clear()


def generate_html_diff(
    text_a: str,
    text_b: str,
    label_a: str = "Before",
    label_b: str = "After",
    context_lines: int = 3
) -> str:
    """
    Generate HTML diff table for two texts.
    
    Per Living Specs Section 1.4.3:
    - Deletions: Struck-through red text background
    - Additions: Bold green text background
    """
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)
    
    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=60)
    
    html_table = differ.make_table(
        lines_a, lines_b,
        fromdesc=label_a,
        todesc=label_b,
        context=True,
        numlines=context_lines
    )
    
    # Apply custom styling
    styled_html = f"""
    <style>
        .diff-container table.diff {{
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            border-collapse: collapse;
            width: 100%;
            background: #0E1117;
        }}
        .diff-container table.diff td {{
            padding: 4px 8px;
            border: 1px solid #31333F;
            vertical-align: top;
        }}
        .diff-container table.diff th {{
            background: #31333F;
            color: #FAFAFA;
            padding: 8px;
            text-align: left;
        }}
        .diff-container .diff_header {{
            background: #1a1a2e;
            color: #888;
        }}
        .diff-container .diff_next {{
            background: #16213e;
        }}
        .diff-container .diff_add {{
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            font-weight: bold;
        }}
        .diff-container .diff_chg {{
            background: rgba(234, 179, 8, 0.2);
            color: #eab308;
        }}
        .diff-container .diff_sub {{
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            text-decoration: line-through;
        }}
    </style>
    <div class="diff-container">
        {html_table}
    </div>
    """
    
    return styled_html


def generate_inline_diff(text_a: str, text_b: str) -> str:
    """Generate inline diff with color spans."""
    differ = difflib.SequenceMatcher(None, text_a, text_b)
    
    result = []
    for opcode, i1, i2, j1, j2 in differ.get_opcodes():
        if opcode == 'equal':
            result.append(html.escape(text_a[i1:i2]))
        elif opcode == 'delete':
            result.append(f'<span style="background:#ef444433;color:#ef4444;text-decoration:line-through;">{html.escape(text_a[i1:i2])}</span>')
        elif opcode == 'insert':
            result.append(f'<span style="background:#22c55e33;color:#22c55e;font-weight:bold;">{html.escape(text_b[j1:j2])}</span>')
        elif opcode == 'replace':
            result.append(f'<span style="background:#ef444433;color:#ef4444;text-decoration:line-through;">{html.escape(text_a[i1:i2])}</span>')
            result.append(f'<span style="background:#22c55e33;color:#22c55e;font-weight:bold;">{html.escape(text_b[j1:j2])}</span>')
    
    return ''.join(result)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_score_badge(score: float) -> str:
    """Generate HTML badge for score with color coding."""
    if score >= 80:
        color = "#22c55e"
        bg = "rgba(34, 197, 94, 0.2)"
        icon = "🟢"
    elif score >= 50:
        color = "#eab308"
        bg = "rgba(234, 179, 8, 0.2)"
        icon = "🟡"
    else:
        color = "#ef4444"
        bg = "rgba(239, 68, 68, 0.2)"
        icon = "🔴"
    
    return f"""
    <span style="
        background: {bg};
        color: {color};
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 12px;
    ">{icon} {score:.1f}</span>
    """


def format_traffic_lights(scores: tuple) -> str:
    """Generate traffic light HTML for tri-state scores."""
    threshold = 50
    lights = []
    for score in scores:
        if score >= threshold:
            lights.append('<span style="color:#22c55e;">●</span>')
        else:
            lights.append('<span style="color:#ef4444;">●</span>')
    return ' '.join(lights)
