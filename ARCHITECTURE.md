# ClawdForDummies - Security Assessment Tool Architecture

## Executive Summary

ClawdForDummies is a **legitimate security self-assessment tool** designed to help non-technical users identify vulnerabilities in their Clawdbot/Moltbot deployments. The tool performs **local-only** security checks on the user's own system and provides clear, actionable guidance on remediation.

**Core Principle:** *This tool ONLY scans the local system it's running on. It never attempts to access external or third-party systems.*

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ClawdForDummies Application                   │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Launcher   │  │  CLI/GUI     │  │   Report Generator   │  │
│  │   Module     │  │  Interface   │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                     │              │
│         └─────────────────┼─────────────────────┘              │
│                           │                                    │
│  ┌────────────────────────┴────────────────────────┐           │
│  │              Security Scanner Engine             │           │
│  │                                                  │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │           │
│  │  │ Port Scan   │  │ Credential  │  │ Config   │ │           │
│  │  │ Module      │  │ Scanner     │  │ Analyzer │ │           │
│  │  └─────────────┘  └─────────────┘  └──────────┘ │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │           │
│  │  │ Process     │  │ File Perm   │  │ Network  │ │           │
│  │  │ Monitor     │  │ Checker     │  │ Analyzer │ │           │
│  │  └─────────────┘  └─────────────┘  └──────────┘ │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Risk Assessment Engine                  │   │
│  │              (CVSS-based scoring system)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Breakdown

| Module | Purpose | User-Facing |
|--------|---------|-------------|
| **Launcher** | Auto-detects OS, sets up environment, runs with appropriate permissions | No |
| **Interface** | Provides CLI and optional GUI for interaction | Yes |
| **Port Scanner** | Checks for exposed ports (18789, etc.) | Indirect |
| **Credential Scanner** | Scans for exposed API keys, tokens, secrets | Indirect |
| **Config Analyzer** | Validates Clawdbot configuration files | Indirect |
| **Process Monitor** | Checks running Clawdbot processes and permissions | Indirect |
| **File Perm Checker** | Validates sensitive file permissions | Indirect |
| **Network Analyzer** | Checks network exposure and firewall rules | Indirect |
| **Risk Engine** | Calculates risk scores, prioritizes findings | Indirect |
| **Report Generator** | Creates human-readable reports with remediation steps | Yes |

---

## 2. Detailed Component Design

### 2.1 Launcher Module (`launcher.py`)

**Purpose:** Zero-configuration startup that works on Windows, macOS, and Linux.

**Key Features:**
- Auto-detects operating system
- Checks Python version (requires 3.8+)
- Verifies required permissions (admin/root for full scan)
- Installs dependencies automatically if missing
- Creates isolated virtual environment (optional)
- Provides one-click/double-click execution

**Entry Points:**
- `start.bat` / `start.sh` - Wrapper scripts for double-click execution
- `python -m clawd_for_dummies` - Python module execution
- `clawd-for-dummies` - Installed CLI command (optional)

### 2.2 Core Scanner Engine (`engine/`)

#### 2.2.1 Port Scanner (`engine/port_scanner.py`)

**Checks:**
- Port 18789 (Clawdbot gateway) binding
- Port accessibility from external networks
- Reverse proxy configuration
- Authentication bypass vulnerability (localhost bypass)

**Detection Logic:**
```python
checks = [
    {
        "name": "clawdbot_gateway_exposed",
        "port": 18789,
        "risk": "CRITICAL",
        "check": "Is port bound to 0.0.0.0 without auth?",
        "remediation": "Configure authentication or bind to 127.0.0.1"
    },
    {
        "name": "reverse_proxy_auth_bypass",
        "port": 18789,
        "risk": "CRITICAL",
        "check": "Is gateway behind reverse proxy without auth?",
        "remediation": "Enable authentication in Clawdbot config"
    }
]
```

#### 2.2.2 Credential Scanner (`engine/credential_scanner.py`)

**Checks:**
- API keys in configuration files (Anthropic, OpenAI, etc.)
- OAuth tokens in environment variables
- Telegram bot tokens
- Slack/Discord webhooks
- Database connection strings
- SSH keys in accessible locations

**Sensitive Patterns:**
- `sk-ant-` (Anthropic API keys)
- `sk-proj-` (OpenAI project keys)
- `xoxb-` / `xoxa-` (Slack tokens)
- Telegram bot token format
- AWS access keys
- Database URIs with passwords

#### 2.2.3 Configuration Analyzer (`engine/config_analyzer.py`)

**Validates:**
- `claude_desktop_config.json` permissions and content
- `settings.json` security settings
- Environment variable exposure
- Docker/container configuration
- Authentication settings

**Key Security Settings to Check:**
```json
{
  "security": {
    "requireAuthentication": true,
    "allowedOrigins": ["specific-domain.com"],
    "enableCORS": false,
    "logLevel": "INFO"
  }
}
```

#### 2.2.4 Process Monitor (`engine/process_monitor.py`)

**Checks:**
- Clawdbot process running as root/admin
- Process arguments exposing sensitive data
- Memory dumps accessibility
- Child processes and their permissions

#### 2.2.5 File Permission Checker (`engine/file_permission_checker.py`)

**Validates:**
- Config file permissions (should be 600, not 644/777)
- Log file accessibility
- Backup file exposure
- World-readable sensitive directories

#### 2.2.6 Network Analyzer (`engine/network_analyzer.py`)

**Checks:**
- Firewall rules for port 18789
- UPnP/NAT-PMP exposure
- Public IP detection
- VPN/proxy detection
- Network interface binding

### 2.3 Risk Assessment Engine (`risk_engine.py`)

**CVSS-inspired Scoring System:**

| Severity | Score | Color | Action |
|----------|-------|-------|--------|
| **CRITICAL** | 9.0-10.0 | 🔴 Red | Immediate action required |
| **HIGH** | 7.0-8.9 | 🟠 Orange | Fix within 24 hours |
| **MEDIUM** | 4.0-6.9 | 🟡 Yellow | Fix within 1 week |
| **LOW** | 0.1-3.9 | 🟢 Green | Fix when convenient |
| **INFO** | 0.0 | ⚪ White | Informational only |

**Risk Calculation Factors:**
- Exploitability (ease of exploitation)
- Impact (data exposure, system compromise)
- Exposure (public vs. local access)
- Privileges required (none vs. admin)

### 2.4 Report Generator (`report_generator.py`)

**Output Formats:**
1. **Console Output** - Colored terminal output with clear messaging
2. **HTML Report** - Rich, visual report with icons and explanations
3. **JSON Report** - Machine-readable for automation
4. **Markdown Report** - Easy to share on GitHub/forums

**Report Sections:**
1. **Executive Summary** - "You're at CRITICAL risk" or "You're relatively safe"
2. **Risk Score** - Overall numerical score with visual gauge
3. **Findings List** - Detailed list of each vulnerability
4. **Remediation Steps** - Step-by-step fix instructions
5. **Resources** - Links to official security guides

---

## 3. User Interface Design

### 3.1 CLI Interface (`interface/cli.py`)

**Design Principles:**
- **No technical jargon** - Use plain English
- **Color-coded output** - Red for danger, green for safe
- **Progress indicators** - Show scan progress
- **Clear action items** - "Do this NOW" messaging

**Example Output:**
```
╔═══════════════════════════════════════════════════════════════╗
║              🔒 CLAWD FOR DUMMIES - Security Scan              ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  OVERALL RISK: CRITICAL (9.2/10)

🔴 CRITICAL ISSUES (Fix IMMEDIATELY):
   1. Your Clawdbot gateway is EXPOSED to the internet!
      → Anyone can access your computer remotely
      → Your API keys and passwords are at risk
      
      HOW TO FIX:
      1. Open your Clawdbot settings
      2. Enable "Require Authentication"
      3. Set a strong password
      4. Restart Clawdbot

🟠 HIGH ISSUES (Fix within 24 hours):
   2. API keys found in plain text
      → Your OpenAI key is visible to any program
      
      HOW TO FIX:
      1. Move API keys to environment variables
      2. Delete the old config file

Press Enter to see detailed report...
```

### 3.2 GUI Interface (`interface/gui.py`) - Optional Phase 2

**Features:**
- One-click scan button
- Visual risk meter
- Expandable finding cards
- Copy-to-clipboard remediation steps
- Export report button

---

## 4. Project Structure

```
clawd-for-dummies/
├── README.md                    # User-facing documentation
├── ARCHITECTURE.md              # This document
├── IMPLEMENTATION.md            # Implementation roadmap
├── requirements.txt             # Python dependencies
├── setup.py                     # Installation script
├── start.bat                    # Windows launcher
├── start.sh                     # Unix launcher
├── start.command               # macOS launcher
│
├── clawd_for_dummies/          # Main package
│   ├── __init__.py
│   ├── __main__.py             # Entry point
│   ├── launcher.py             # Startup logic
│   ├── scanner.py              # Main scanner orchestrator
│   ├── risk_engine.py          # Risk scoring
│   ├── report_generator.py     # Output generation
│   │
│   ├── engine/                 # Scanner modules
│   │   ├── __init__.py
│   │   ├── base_scanner.py     # Abstract base class
│   │   ├── port_scanner.py
│   │   ├── credential_scanner.py
│   │   ├── config_analyzer.py
│   │   ├── process_monitor.py
│   │   ├── file_permission_checker.py
│   │   └── network_analyzer.py
│   │
│   ├── interface/              # User interfaces
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── gui.py              # Future
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── finding.py          # Vulnerability finding
│   │   ├── risk_score.py       # Risk scoring model
│   │   └── scan_result.py      # Complete scan result
│   │
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── validators.py
│   │   └── system_info.py
│   │
│   └── templates/              # Report templates
│       ├── html_report.html
│       └── markdown_report.md
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_port_scanner.py
│   ├── test_credential_scanner.py
│   └── ...
│
└── docs/                       # Additional documentation
    ├── USER_GUIDE.md
    ├── SECURITY.md
    └── FAQ.md
```

---

## 5. Data Models

### 5.1 Finding Model

```python
@dataclass
class Finding:
    """Represents a security finding/vulnerability."""
    
    id: str                      # Unique identifier
    title: str                   # Human-readable title
    description: str             # Detailed description
    severity: Severity           # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: Category           # PORT, CREDENTIAL, CONFIG, etc.
    cvss_score: float           # 0.0 - 10.0
    
    # Technical details
    evidence: Dict[str, Any]     # Proof of vulnerability
    location: str               # Where found
    
    # Remediation
    remediation: str            # How to fix
    remediation_steps: List[str] # Step-by-step instructions
    reference_links: List[str]  # Official documentation
    
    # Metadata
    timestamp: datetime
    scanner_version: str
```

### 5.2 Scan Result Model

```python
@dataclass
class ScanResult:
    """Complete result of a security scan."""
    
    scan_id: str
    timestamp: datetime
    duration_seconds: float
    system_info: SystemInfo
    
    findings: List[Finding]
    overall_risk_score: float
    risk_level: RiskLevel
    
    # Summary counts
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    
    # Quick actions
    immediate_actions: List[str]
```

---

## 6. Security & Ethics

### 6.1 Design Principles

1. **Local-Only Operation** - Never scans external systems
2. **Read-Only** - Never modifies system configuration
3. **Transparent** - All operations are logged and visible
4. **No Data Collection** - No telemetry, no external calls
5. **Open Source** - Full transparency in how it works

### 6.2 User Warnings

The tool must display on every run:
```
⚠️  IMPORTANT: This tool ONLY scans YOUR computer.
    It will NOT access any external systems.
    All scanning is done locally and safely.
```

### 6.3 Legal Disclaimer

Include in README and startup:
```
This tool is for educational and self-assessment purposes only.
Users are responsible for ensuring they only scan systems they own
or have explicit permission to scan.
```

---

## 7. Dependencies

**Core Dependencies:**
```
psutil>=5.9.0      # Process and system monitoring
requests>=2.28.0   # HTTP requests for local testing
colorama>=0.4.6    # Cross-platform colored output
rich>=13.0.0       # Beautiful terminal output (optional)
pyyaml>=6.0        # YAML config parsing
```

**Optional Dependencies:**
```
pyinstaller>=5.0   # Create standalone executables
tkinter            # GUI interface (built-in)
```

---

## 8. Design Patterns Used

| Pattern | Application |
|---------|-------------|
| **Strategy Pattern** | Different scanner implementations |
| **Observer Pattern** | Progress reporting during scans |
| **Factory Pattern** | Report format generation |
| **Singleton Pattern** | Configuration manager |
| **Template Method** | Base scanner with common workflow |

---

## 9. Error Handling Strategy

**Graceful Degradation:**
- If one scanner fails, continue with others
- Log errors but don't crash
- Provide partial results when possible

**Permission Handling:**
- Detect if admin/root is needed
- Explain why elevated permissions help
- Offer to continue with limited scan

---

## 10. Future Enhancements

**Phase 2:**
- GUI interface with tkinter/PyQt
- Scheduled/automated scans
- Historical scan comparison
- Integration with Clawdbot API for auto-remediation

**Phase 3:**
- Network-wide scanning (with permission)
- SIEM integration
- Compliance reporting (SOC2, ISO27001)

---

*Document Version: 1.0*
*Last Updated: 2026-01-28*
*Status: Draft for Review*
