import streamlit as st
import asyncio
import os
import logging

from agents import Runner
from main import research_agent,rewrite_agent
from formatter import generate_html
from validator import parse_and_validate_report
from pdf_generator import save_pdf
from emailer import send_email

if "loading" not in st.session_state:
    st.session_state["loading"] = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global Styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background: #09090b;
    color: #e4e4e7;
}

/* ── Block container ── */
.block-container {
    padding: 2rem 2.5rem 3rem;
    max-width: 1400px;
}

/* ── Header ── */
.app-header {
    position: relative;
    padding: 2rem 0 1.75rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #27272a;
    overflow: hidden;
}
.app-header-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4f46e5 0%, #818cf8 40%, #c084fc 70%, transparent 100%);
}
.app-header-top {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 0.6rem;
}
.app-header h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    font-weight: 600;
    color: #f4f4f5;
    letter-spacing: -0.5px;
    margin: 0;
}
.app-header-version {
    font-size: 0.7rem;
    color: #52525b;
    font-family: 'IBM Plex Mono', monospace;
    background: #18181b;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    padding: 2px 8px;
    letter-spacing: 0.06em;
}
.app-header-sub {
    font-size: 0.82rem;
    color: #71717a;
    font-family: 'IBM Plex Sans', sans-serif;
    margin-bottom: 1.2rem;
}
.app-header-pills {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.header-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    border: 1px solid #27272a;
    color: #71717a;
    background: #18181b;
}
.header-pill .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #4f46e5;
    display: inline-block;
    animation: pulse-dot 2s ease-in-out infinite;
}
.header-pill .dot-green {
    background: #22c55e;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.75); }
}

/* ── Panel labels ── */
h2, h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #52525b !important;
    margin-bottom: 1rem !important;
}

/* ── Input ── */
.stTextInput > div > div > input {
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 6px !important;
    color: #e4e4e7 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.85rem !important;
    transition: border-color 0.15s;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}
.stTextInput label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #a1a1aa !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── Buttons ── */
.stButton > button {
    width: 100%;
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 6px !important;
    color: #d4d4d8 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.15s ease !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: #27272a !important;
    border-color: #6366f1 !important;
    color: #a5b4fc !important;
}
.stButton > button:active {
    transform: scale(0.98) !important;
}

/* ── Primary button (generate) ── */
div[data-testid="stButton"]:first-of-type > button {
    background: #4f46e5 !important;
    border-color: #4f46e5 !important;
    color: #fff !important;
}
div[data-testid="stButton"]:first-of-type > button:hover {
    background: #6366f1 !important;
    border-color: #6366f1 !important;
    color: #fff !important;
}

/* ── Divider ── */
hr {
    border-color: #27272a !important;
    margin: 1.25rem 0 !important;
}

/* ── Status badges ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.badge-ready  { background: #14532d; color: #86efac; border: 1px solid #166534; }
.badge-empty  { background: #18181b; color: #52525b; border: 1px solid #27272a; }
.badge-error  { background: #450a0a; color: #fca5a5; border: 1px solid #7f1d1d; }

/* ── Alert overrides ── */
.stAlert {
    border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #6366f1 !important;
}

/* ── Preview panel border ── */
.preview-panel {
    border: 1px solid #27272a;
    border-radius: 8px;
    overflow: hidden;
    background: #18181b;
    min-height: 500px;
}
.preview-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 500px;
    color: #3f3f46;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    gap: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ─────────────────────────────────────────────────────────────────

def run_agent(prompt: str) -> dict:
    """Run the research agent and return a validated report dict."""
    result = asyncio.run(Runner.run(research_agent, prompt))
    return parse_and_validate_report(result.final_output)


def set_error(msg: str):
    st.session_state["error"] = msg


def clear_error():
    st.session_state.pop("error", None)

def run_rewrite(prompt: str):
    result = asyncio.run(Runner.run(rewrite_agent, prompt))
    return parse_and_validate_report(result.final_output)


# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-header-accent"></div>
    <div class="app-header-top">
        <h1>Research Assistant</h1> 
    </div>
    <div class="app-header-sub">
        AI-powered research reports — generate, refine, and deliver in minutes
    </div>
    <div class="app-header-pills">
        <span class="header-pill"><span class="dot"></span>arXiv + Web Search</span>
        <span class="header-pill"><span class="dot dot-green"></span>Agent Pipeline Active</span>
        <span class="header-pill">PDF · Email Delivery</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ──────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2.4], gap="large")

# ── LEFT PANEL ──────────────────────────────────────────────────────────────
with left:
    st.markdown("### Controls")

    topic = st.text_input(
        "Topic",
        placeholder="e.g. Quantum computing advances 2026",
        help="Enter a research topic to generate a structured report.",
    )

    generate_clicked = st.button(
        "⚡ Generate Report",
        use_container_width=True,
        disabled=st.session_state["loading"]
    )

    if generate_clicked:
        if not topic.strip():
            st.warning("Please enter a topic before generating.")
        else:
            clear_error()
            st.session_state["loading"] = True

            with st.spinner("Researching & writing report…"):
                try:
                    report = run_agent(topic.strip())
                    st.session_state["report"] = report
                    st.session_state["html"] = generate_html(report)
                    st.session_state["topic"] = topic.strip()
                    
                    st.session_state["pdf_ready"] = False

                    st.toast("Report generated")  # 👈 NEW

                except Exception as e:
                    logger.exception("Report generation failed")
                    set_error(f"Generation failed: {e}")

            st.session_state["loading"] = False

    # ── Error display ────────────────────────────────────────────────────────
    if "error" in st.session_state:
        st.error(st.session_state["error"])

    # ── Status badge ─────────────────────────────────────────────────────────
    if "report" in st.session_state:
        st.markdown(
            '<div class="status-badge badge-ready">● Report Ready</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-badge badge-empty">○ No Report</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Regenerate section (only shown when report exists) ───────────────────
    if "report" in st.session_state:
        st.markdown("### Regenerate")

        # ── Existing buttons ──
        regen_summary = st.button(
            "↺ Summary",
            use_container_width=True,
            disabled=st.session_state["loading"]
        )

        regen_findings = st.button(
            "↺ Key Findings",
            use_container_width=True,
            disabled=st.session_state["loading"]
        )

        # ── NEW: Select + regenerate single finding ──
    
        findings = st.session_state["report"]["key_findings"]
        
        if not findings:
            st.info("No findings available.")
        else:
            selected = st.selectbox(
                "Select finding",
                options=list(range(len(findings))),
                format_func=lambda i: f"{i+1}. {findings[i]['title'][:40]}"
            )

        regen_single = st.button(
            "↺ Regenerate Selected Finding",
            use_container_width=True,
            disabled=st.session_state["loading"]
        )

        # ── Summary regen ──
        if regen_summary:
            clear_error()
            with st.spinner("Rewriting summary…"):
                try:
                    report = st.session_state["report"]
                    updated = run_rewrite(f"Rewrite only the summary:\n{report}")
                    report["summary"] = updated.get("summary", report["summary"])
                    st.session_state["report"] = report
                    st.session_state["html"] = generate_html(report)
                    st.success("Summary regenerated.")
                except Exception as e:
                    logger.exception("Summary regen failed")
                    set_error(f"Summary regen failed: {e}")

        # ── Findings regen ──
        if regen_findings:
            clear_error()
            with st.spinner("Rewriting key findings…"):
                try:
                    report = st.session_state["report"]
                    updated = run_rewrite(f"Rewrite the key findings:\n{report}")
                    report["key_findings"] = updated.get("key_findings", report["key_findings"])
                    st.session_state["report"] = report
                    st.session_state["html"] = generate_html(report)
                    st.success("Key findings regenerated.")
                except Exception as e:
                    logger.exception("Findings regen failed")
                    set_error(f"Findings regen failed: {e}")

        # ── NEW: Single finding regen ──
        if regen_single:
            clear_error()
            with st.spinner("Rewriting selected finding…"):
                try:
                    report = st.session_state["report"]

                    prompt = f"Rewrite only finding index {selected} in this report:\n{report}"
                    updated = run_rewrite(prompt)

                    report["key_findings"][selected] = updated["key_findings"][selected]

                    st.session_state["report"] = report
                    st.session_state["html"] = generate_html(report)

                    st.success("Finding updated.")
                except Exception as e:
                    logger.exception("Single finding regen failed")
                    set_error(f"Finding regen failed: {e}")

        st.divider()

        
        st.markdown("### Export")
 
        if "report" in st.session_state:
            try:
                pdf_path = "report.pdf"

                if not st.session_state.get("pdf_ready", False):
                    save_pdf(st.session_state["html"], pdf_path)
                    st.session_state["pdf_ready"] = True

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "⬇ Download PDF",
                        f,
                        file_name="report.pdf",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"PDF generation failed: {e}")

        # ── Email ────────────────────────────────────────────────────────────
        st.markdown("### Deliver")

        recipient = st.text_input(
            "Recipient Email",
            value=os.getenv("EMAIL_USER", ""),
            placeholder="recipient@example.com",
        )

        send_clicked = st.button(
            "✉ Send as PDF",
            use_container_width=True,
            disabled=st.session_state["loading"]
        )

        if send_clicked:
            if not recipient.strip():
                st.warning("Enter a recipient email address.")
            else:
                clear_error()
                with st.spinner("Generating PDF and sending email…"):
                    try:
                        pdf_path = "report.pdf"
                        if not st.session_state.get("pdf_ready", False):
                            save_pdf(st.session_state["html"], pdf_path)
                            st.session_state["pdf_ready"] = True
                        send_email(
                            sender_email=os.getenv("EMAIL_USER"),
                            app_password=os.getenv("EMAIL_PASS"),
                            receiver_email=recipient.strip(),
                            file_path=pdf_path,
                        )
                        st.success(f"Email sent to **{recipient.strip()}**!")
                    except Exception as e:
                        logger.exception("Email send failed")
                        set_error(f"Email failed: {e}")

# ── RIGHT PANEL ──────────────────────────────────────────────────────────────
with right:
    topic_label = st.session_state.get("topic", "")
    header = f"### Preview — {topic_label}" if topic_label else "### Preview"
    st.markdown(header)

    if "html" in st.session_state:
        st.components.v1.html(
            st.session_state["html"],
            height=920,
            scrolling=True,
        )
    else:
        st.markdown("""
<div class="preview-panel">
    <div class="preview-empty">
        <span>▤</span>
        <span>No report generated yet</span>
    </div>
</div>
""", unsafe_allow_html=True)