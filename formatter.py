from datetime import datetime


def generate_html(report: dict) -> str:
    date_str = datetime.now().strftime("%B %d, %Y")

    confidence_colors = {
        "high": "#16a34a",
        "empirical evidence": "#16a34a",
        "foundational analysis": "#2563eb",
        "theoretical framework": "#7c3aed",
        "review & agenda": "#d97706",
        "risk assessment": "#dc2626",
    }

    def confidence_color(conf: str) -> str:
        key = conf.lower().strip()
        for k, v in confidence_colors.items():
            if k in key:
                return v
        return "#6b7280"

    findings_html = ""
    for i, f in enumerate(report.get("key_findings", [])):
        color = confidence_color(f.get("confidence", ""))
        findings_html += f"""
        <div class="finding">
            <div class="finding-number">{str(i + 1).zfill(2)}</div>
            <div class="finding-body">
                <h3>{f.get('title', '')}</h3>
                <p>{f.get('explanation', '')}</p>
                <span class="badge" style="background:{color}20; color:{color}; border:1px solid {color}40">
                    {f.get('confidence', '')}
                </span>
            </div>
        </div>
        """

    arxiv_sources = [s for s in report.get("sources", []) if s.get("source_type") == "arxiv"]
    web_sources = [s for s in report.get("sources", []) if s.get("source_type") != "arxiv"]

    def source_item(s):
        authors = ", ".join(s.get("authors", [])[:2])
        if len(s.get("authors", [])) > 2:
            authors += " et al."
        date = s.get("published_date", "")
        meta = " · ".join(filter(None, [authors, date]))
        return f"""
        <li>
            <a href="{s.get('url', '#')}">{s.get('title', 'Untitled')}</a>
            {f'<span class="source-meta">{meta}</span>' if meta else ''}
        </li>
        """

    arxiv_html = "".join(source_item(s) for s in arxiv_sources)
    web_html = "".join(source_item(s) for s in web_sources)

    sources_html = ""
    if arxiv_sources:
        sources_html += f"<h3 class='source-group'>arXiv Papers</h3><ul>{''.join(source_item(s) for s in arxiv_sources)}</ul>"
    if web_sources:
        sources_html += f"<h3 class='source-group'>Web Sources</h3><ul>{''.join(source_item(s) for s in web_sources)}</ul>"

    html = f"""
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: Georgia, 'Times New Roman', serif;
            background: #f8f7f4;
            color: #1a1a1a;
            padding: 0;
        }}

        .page {{
            max-width: 720px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
        }}

        /* Header */
        .header {{
            background: #0f172a;
            padding: 48px 56px 40px;
            color: white;
        }}

        .header-meta {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #94a3b8;
            margin-bottom: 20px;
        }}

        .header h1 {{
            font-size: 32px;
            font-weight: normal;
            line-height: 1.25;
            color: #f1f5f9;
            margin-bottom: 0;
        }}

        .header-date {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 12px;
            color: #64748b;
            margin-top: 16px;
        }}

        /* Body */
        .body {{
            padding: 48px 56px;
        }}

        /* Summary */
        .summary-block {{
            border-left: 3px solid #0f172a;
            padding-left: 20px;
            margin-bottom: 48px;
        }}

        .summary-block .label {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #94a3b8;
            margin-bottom: 10px;
        }}

        .summary-block p {{
            font-size: 16px;
            line-height: 1.75;
            color: #334155;
        }}

        /* Section headers */
        .section-label {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #94a3b8;
            margin-bottom: 24px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e2e8f0;
        }}

        /* Findings */
        .findings {{ margin-bottom: 48px; }}

        .finding {{
            display: flex;
            gap: 20px;
            margin-bottom: 32px;
            padding-bottom: 32px;
            border-bottom: 1px solid #f1f5f9;
        }}

        .finding:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}

        .finding-number {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: #cbd5e1;
            min-width: 28px;
            padding-top: 3px;
        }}

        .finding-body h3 {{
            font-size: 17px;
            font-weight: bold;
            color: #0f172a;
            margin-bottom: 10px;
            line-height: 1.3;
        }}

        .finding-body p {{
            font-size: 14px;
            line-height: 1.75;
            color: #475569;
            margin-bottom: 12px;
        }}

        .badge {{
            display: inline-block;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 10px;
            letter-spacing: 0.5px;
            padding: 3px 10px;
            border-radius: 999px;
            font-weight: 500;
        }}

        /* Why it matters */
        .matters-block {{
            background: #f8faff;
            border: 1px solid #e0e7ff;
            border-radius: 8px;
            padding: 28px 32px;
            margin-bottom: 48px;
        }}

        .matters-block p {{
            font-size: 15px;
            line-height: 1.8;
            color: #334155;
        }}

        /* Sources */
        .sources-block {{ margin-bottom: 48px; }}

        .source-group {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #94a3b8;
            margin: 20px 0 12px;
        }}

        .sources-block ul {{
            list-style: none;
            padding: 0;
        }}

        .sources-block li {{
            padding: 10px 0;
            border-bottom: 1px solid #f1f5f9;
            font-size: 13px;
        }}

        .sources-block li:last-child {{ border-bottom: none; }}

        .sources-block a {{
            color: #1d4ed8;
            text-decoration: none;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.4;
        }}

        .source-meta {{
            display: block;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 11px;
            color: #94a3b8;
            margin-top: 2px;
        }}

        /* Footer */
        .footer {{
            background: #f8f7f4;
            padding: 24px 56px;
            border-top: 1px solid #e2e8f0;
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
        }}
    </style>
    </head>
    <body>
    <div class="page">

        <div class="header">
            <div class="header-meta">Research Digest</div>
            <h1>{report.get('title', 'Research Report')}</h1>
            <div class="header-date">{date_str}</div>
        </div>

        <div class="body">

            <div class="summary-block">
                <div class="label">Overview</div>
                <p>{report.get('summary', '')}</p>
            </div>

            <div class="findings">
                <div class="section-label">Key Findings</div>
                {findings_html}
            </div>

            <div class="matters-block">
                <div class="section-label" style="margin-bottom:14px">Why It Matters</div>
                <p>{report.get('why_it_matters', '')}</p>
            </div>

            <div class="sources-block">
                <div class="section-label">Sources</div>
                {sources_html}
            </div>

        </div>

        <div class="footer">
            Generated by Research Agent &nbsp;·&nbsp; {date_str}
        </div>

    </div>
    </body>
    </html>
    """

    return html