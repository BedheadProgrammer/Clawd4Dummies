"""
Report generator for HTML, JSON, and Markdown output formats.
"""

import html as html_escape
import json

from clawd_for_dummies.models.scan_result import ScanResult


class ReportGenerator:
    """Generates security scan reports in various formats."""

    def generate_html(self, result: ScanResult) -> str:
        """
        Generate an HTML report from scan results. This method creates a complete
        HTML document with inline CSS styling for the security report.
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClawdForDummies Security Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .risk-meter {{
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .risk-critical {{ background-color: #fee; border: 2px solid #c00; }}
        .risk-high {{ background-color: #fff3cd; border: 2px solid #f0ad4e; }}
        .risk-medium {{ background-color: #fffbe6; border: 2px solid #ffc107; }}
        .risk-low {{ background-color: #d4edda; border: 2px solid #28a745; }}
        .risk-safe {{ background-color: #d1ecf1; border: 2px solid #17a2b8; }}
        .finding {{
            background: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .finding-critical {{ border-left: 4px solid #dc3545; }}
        .finding-high {{ border-left: 4px solid #fd7e14; }}
        .finding-medium {{ border-left: 4px solid #ffc107; }}
        .finding-low {{ border-left: 4px solid #28a745; }}
        .finding-info {{ border-left: 4px solid #6c757d; }}
        .severity {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .severity-critical {{ background: #dc3545; color: white; }}
        .severity-high {{ background: #fd7e14; color: white; }}
        .severity-medium {{ background: #ffc107; color: black; }}
        .severity-low {{ background: #28a745; color: white; }}
        .severity-info {{ background: #6c757d; color: white; }}
        .remediation {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .fix-prompt {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
            position: relative;
        }}
        .fix-prompt-header {{
            color: #667eea;
            font-weight: bold;
            margin-bottom: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }}
        .summary-item {{
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: white;
        }}
        .summary-count {{
            font-size: 32px;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ClawdForDummies Security Report</h1>
        <p>Generated on: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Scan ID: {result.scan_id}</p>
    </div>

    <div class="risk-meter risk-{result.risk_level.value}">
        <h2>Overall Risk: {result.risk_level.value.upper()}</h2>
        <p style="font-size: 48px; margin: 10px 0;">{result.risk_level.indicator}</p>
        <p>Risk Score: {result.overall_risk_score:.1f}/10</p>
        <p>{result.risk_level.message}</p>
    </div>

    <div class="summary">
        <div class="summary-item">
            <div class="summary-count" style="color: #dc3545;">{result.critical_count}</div>
            <div>Critical</div>
        </div>
        <div class="summary-item">
            <div class="summary-count" style="color: #fd7e14;">{result.high_count}</div>
            <div>High</div>
        </div>
        <div class="summary-item">
            <div class="summary-count" style="color: #ffc107;">{result.medium_count}</div>
            <div>Medium</div>
        </div>
        <div class="summary-item">
            <div class="summary-count" style="color: #28a745;">{result.low_count}</div>
            <div>Low</div>
        </div>
        <div class="summary-item">
            <div class="summary-count" style="color: #6c757d;">{result.info_count}</div>
            <div>Info</div>
        </div>
    </div>
"""

        if result.findings:
            html += "    <h2>Detailed Findings</h2>\n"

            for finding in result.findings:
                fix_prompt_html = ""
                if finding.fix_prompt:
                    # Escape HTML to prevent XSS
                    escaped_prompt = html_escape.escape(finding.fix_prompt)
                    fix_prompt_html = f'''
        <div class="fix-prompt" role="region" aria-label="AI Fix Prompt">
            <h5 class="fix-prompt-header">AI Fix Prompt (copy and paste to your AI assistant)</h5>
            {escaped_prompt}
        </div>'''

                html += f"""
    <div class="finding finding-{finding.severity.value}">
        <span class="severity severity-{finding.severity.value}">{finding.severity.value.upper()}</span>
        <h3>{html_escape.escape(finding.title)}</h3>
        <p><strong>Category:</strong> {html_escape.escape(finding.category.display_name)}</p>
        <p>{html_escape.escape(finding.description)}</p>

        {f'<p><strong>Location:</strong> {html_escape.escape(finding.location)}</p>' if finding.location else ''}

        <div class="remediation">
            <h4>How to Fix</h4>
            <p>{html_escape.escape(finding.remediation)}</p>

            {f'<ol>{"".join(f"<li>{html_escape.escape(step)}</li>" for step in finding.remediation_steps)}</ol>' if finding.remediation_steps else ''}
        </div>

        {fix_prompt_html}

        {f'<p><strong>Learn more:</strong> {" | ".join(f"<a href=\"{html_escape.escape(link)}\">{html_escape.escape(link)}</a>" for link in finding.reference_links)}</p>' if finding.reference_links else ''}
    </div>
"""
        else:
            html += """
    <div class="finding" style="text-align: center;">
        <h2>No Security Issues Found!</h2>
        <p>Your system looks safe. No vulnerabilities were detected.</p>
    </div>
"""

        html += f"""
    <div class="footer">
        <p>Scan completed in {result.duration_seconds:.2f} seconds</p>
        <p>Scanner version: {result.scanner_version}</p>
        <p>For more information: <a href="https://github.com/yourusername/clawd-for-dummies">ClawdForDummies on GitHub</a></p>
    </div>
</body>
</html>
"""

        return html

    def generate_json(self, result: ScanResult) -> str:
        return json.dumps(result.to_dict(), indent=2)

    def generate_markdown(self, result: ScanResult) -> str:
        md = f"""# ClawdForDummies Security Report

**Generated:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Scan ID:** {result.scan_id}
**Scanner Version:** {result.scanner_version}

---

## Overall Risk: {result.risk_level.value.upper()} {result.risk_level.indicator}

**Risk Score:** {result.overall_risk_score:.1f}/10

{result.risk_level.message}

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | {result.critical_count} |
| High | {result.high_count} |
| Medium | {result.medium_count} |
| Low | {result.low_count} |
| Info | {result.info_count} |
| **Total** | **{result.total_count}** |

---

"""

        if result.findings:
            md += "## Detailed Findings\n\n"

            for finding in result.findings:
                md += f"""### {finding.severity.indicator} {finding.title}

**Severity:** {finding.severity.value.upper()}
**Category:** {finding.category.display_name}
**Risk Score:** {finding.cvss_score}/10

{f"**Location:** {finding.location}  " if finding.location else ""}

{finding.description}

#### Remediation

{finding.remediation}

"""

                if finding.remediation_steps:
                    md += "**Steps:**\n"
                    for i, step in enumerate(finding.remediation_steps, 1):
                        md += f"{i}. {step}\n"
                    md += "\n"

                if finding.fix_prompt:
                    md += "#### AI Fix Prompt\n\n"
                    md += "Copy and paste this prompt to your AI assistant:\n\n"
                    md += f"```\n{finding.fix_prompt}\n```\n\n"

                if finding.reference_links:
                    md += "**References:**\n"
                    for link in finding.reference_links:
                        md += f"- {link}\n"
                    md += "\n"

                md += "---\n\n"
        else:
            md += """## No Security Issues Found

Your system looks safe. No vulnerabilities were detected.

---

"""

        md += f"""## Scan Details

- **Duration:** {result.duration_seconds:.2f} seconds
- **Scanner Version:** {result.scanner_version}

For more information, visit: https://github.com/yourusername/clawd-for-dummies
"""

        return md
