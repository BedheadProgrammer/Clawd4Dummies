# ClawdForDummies

**Security Assessment Tool for Clawdbot/Moltbot Deployments**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security](https://img.shields.io/badge/security-focused-red.svg)](https://github.com/yourusername/clawd-for-dummies)

---

## Important Security Notice

ClawdForDummies is a legitimate security self-assessment tool designed for local system evaluation.

**Key Characteristics:**

- Scans only the local system where it is executed
- Does not access external or third-party systems
- Operates in read-only mode and never modifies system configuration
- Fully open source for complete transparency
- No telemetry or data collection

By using this tool, you agree to only scan systems you own or have explicit permission to scan.

---

## Overview

ClawdForDummies is a security assessment tool designed for users who need to verify the security posture of their [Clawdbot](https://github.com/jasondsmith72/Clawdbot) or Moltbot deployment.

### Background

Security research has identified that approximately 900-1,000+ Clawdbot instances are publicly exposed without authentication, presenting critical security risks including:

- API key exposure (Anthropic, OpenAI, and other providers)
- Private conversation history leakage
- OAuth token compromise
- Remote code execution vulnerabilities
- Unauthorized file system access

ClawdForDummies enables users to assess whether their systems are vulnerable to these exposures.

---

## Quick Start

### Option 1: Double-Click Launch

1. Download the latest release for your platform
2. Extract the archive
3. Execute the appropriate launcher:
   - **Windows:** `start.bat`
   - **macOS:** `start.command`
   - **Linux:** `start.sh`

### Option 2: Python Installation

```bash
git clone https://github.com/yourusername/clawd-for-dummies.git
cd clawd-for-dummies

# Install the package
pip install -e .

# Run the scanner
clawd-for-dummies
```

### Option 3: Standalone Executable

Download pre-built executables from the [Releases](https://github.com/yourusername/clawd-for-dummies/releases) page:

- `clawd-for-dummies-windows.exe`
- `clawd-for-dummies-macos`
- `clawd-for-dummies-linux`

---

## Security Checks

ClawdForDummies performs comprehensive security assessments across multiple categories:

### Port Scanner
- **Exposed Gateway Detection:** Verifies if Clawdbot port (18789) is accessible from the network
- **Authentication Bypass Testing:** Checks for reverse proxy authentication bypass vulnerabilities
- **Binding Configuration:** Confirms gateway is bound to localhost only

### Credential Scanner
- **API Key Exposure:** Detects exposed Anthropic, OpenAI, and other API keys
- **Token Detection:** Identifies Slack, Discord, Telegram, and other service tokens
- **Environment Variables:** Checks for credentials stored in environment variables
- **Configuration File Scanning:** Scans configuration files for hardcoded secrets

### Configuration Analyzer
- **Authentication Settings:** Verifies authentication is enabled
- **CORS Configuration:** Checks for overly permissive CORS settings
- **Allowed Origins:** Validates origin restrictions
- **Logging Settings:** Detects verbose logging that may expose sensitive data

### Process Monitor
- **Privilege Check:** Detects if Clawdbot runs with elevated privileges (root/admin)
- **Command Line Secrets:** Checks for secrets exposed in process arguments

### File Permission Checker
- **World-Readable Files:** Identifies configuration files readable by other users
- **World-Writable Files:** Detects files writable by anyone
- **Backup Files:** Locates backup files that may contain sensitive data

### Network Analyzer
- **Public IP Detection:** Determines if the system has a public IP address
- **Firewall Status:** Verifies firewall is enabled
- **Port Forwarding:** Identifies UPnP/NAT-PMP exposure risks

---

## Usage

### Basic Commands

```bash
# Run full security scan
clawd-for-dummies

# Run quick scan (ports and configuration only)
clawd-for-dummies --quick

# Generate JSON report for automation
clawd-for-dummies --output json --output-file report.json

# Enable verbose output with debug information
clawd-for-dummies --verbose
```

---

## Example Output

```
+====================================================================+
|           CLAWD FOR DUMMIES - Security Scan Results                |
+====================================================================+

SYSTEM INFORMATION:
  Platform: Windows 10
  User: john_doe
  Admin Privileges: No

====================================================================
OVERALL RISK: CRITICAL
   Risk Score: 9.2/10
   Immediate action required
====================================================================

FINDINGS SUMMARY:
   Critical: 1
   High:     2
   Medium:   1
   Low:      0
   Info:     1

CRITICAL ISSUES:

[CRITICAL] Clawdbot Gateway Exposed to Network
   The Clawdbot gateway (port 18789) is bound to 0.0.0.0, making it
   accessible from any computer on the network or internet.

   REMEDIATION:
   1. Open your Clawdbot configuration file
   2. Change 'bind' from '0.0.0.0' to '127.0.0.1'
   3. Restart Clawdbot

====================================================================
Scan completed in 5.23 seconds
Scanner version: 1.0.0
```

---

## Common Issues and Remediation

### Gateway Exposed to Network

**Problem:** Port 18789 is bound to 0.0.0.0 (all interfaces)

**Solution:**
```bash
# Edit your configuration file
# Change:
# Restart Clawdbot
```

### Authentication Not Enabled

**Problem:** The gateway accepts connections without authentication

**Solution:**
```json
{
  "security": {
}
```

### API Key Exposed in Configuration

**Problem:** API key stored in plain text within configuration file

**Solution:**
```bash
# Remove the key from the configuration file
# Use environment variables instead:
export ANTHROPIC_API_KEY="your-key-here"

# Alternatively, use a secrets manager
```

---

## Architecture

```
clawd_for_dummies/
├── __init__.py
├── __main__.py             # CLI entry point
├── scanner.py              # Main scanner orchestrator
├── report_generator.py     # Report generation
│
├── engine/                 # Scanner modules
│   ├── base_scanner.py     # Abstract base class
│   ├── port_scanner.py
│   ├── credential_scanner.py
│   ├── config_analyzer.py
│   ├── process_monitor.py
│   ├── file_permission_checker.py
│   └── network_analyzer.py
│
├── interface/              # User interfaces
│   └── cli.py
│
├── models/                 # Data models
│   ├── finding.py
│   ├── scan_result.py
│   └── system_info.py
│
└── utils/                  # Utilities
    └── logger.py
```

---

## Security and Privacy

### Data Handling

This tool is designed with privacy as a core principle:

- No data is transmitted to external servers
- No telemetry or usage data is collected
- Credentials found during scanning are masked in reports (only first/last 4 characters displayed)
- All operations are performed locally and logged for transparency

### Operational Constraints

- Read-only operation: the tool never modifies system configuration
- Local-only scanning: external systems are never accessed
- Open source codebase: all functionality can be audited

---

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/clawd-for-dummies.git
cd clawd-for-dummies

# Run tests
pytest

# Run tests with coverage
pytest --cov=clawd_for_dummies
```



---

## License

This project is licensed under the MIT License. 

---

## Acknowledgments

- Security researchers who identified Clawdbot vulnerabilities
- The Clawdbot/Moltbot community
- Projects that inspired this tool: [Lynis](https://cisofy.com/lynis/), [Nmap](https://nmap.org/)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/clawd-for-dummies/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/clawd-for-dummies/discussions)

---

## Disclaimer

This tool is provided as-is for educational and self-assessment purposes. The authors assume no responsibility for any damage or issues resulting from the use of this tool. Users are responsible for ensuring they have proper authorization before scanning any system.

---

*Version 1.0.0*
