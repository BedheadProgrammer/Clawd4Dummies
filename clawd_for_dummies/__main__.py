#!/usr/bin/env python3
"""
Main entry point for the ClawdForDummies security scanner CLI.
"""

import argparse
import sys
from typing import Optional

from clawd_for_dummies.models.system_info import SystemInfo
from clawd_for_dummies.interface.cli import CLI
from clawd_for_dummies.scanner import SecurityScanner
from clawd_for_dummies.utils.logger import setup_logging


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clawd-for-dummies",
        description="""
        ClawdForDummies - Security Assessment Tool for Clawdbot/Moltbot

        A user-friendly scanner that helps identify vulnerabilities in your
        Clawdbot/Moltbot deployment. This tool ONLY scans your local system.
        """,
        epilog="""
        Examples:
          %(prog)s                    # Run full scan with console output
          %(prog)s --quick            # Run quick scan (faster, less thorough)
          %(prog)s --output html      # Generate HTML report
          %(prog)s --output-file report.html  # Save report to file
          %(prog)s --verbose          # Show detailed output

        For more information: https://github.com/yourusername/clawd-for-dummies
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    scan_group = parser.add_argument_group("Scan Options")
    scan_group.add_argument(
        "--quick",
        action="store_true",
        help="Run quick scan (port + config only, faster but less thorough)",
    )
    scan_group.add_argument(
        "--full",
        action="store_true",
        default=True,
        help="Run full scan (all modules) [default]",
    )
    scan_group.add_argument(
        "--modules",
        nargs="+",
        choices=[
            "port",
            "credential",
            "config",
            "process",
            "permission",
            "network",
            "clawdbot",
        ],
        metavar="MODULE",
        help="Run specific scan modules only",
    )

    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--output",
        "-o",
        choices=["console", "html", "json", "markdown"],
        default="console",
        help="Output format [default: console]",
    )
    output_group.add_argument(
        "--output-file",
        "-f",
        metavar="FILE",
        help="Save report to file (optional, defaults to stdout for console)",
    )
    output_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output including debug information",
    )
    output_group.add_argument(
        "--silent",
        "-s",
        action="store_true",
        help="Minimal output (errors only)",
    )

    info_group = parser.add_argument_group("Information")
    info_group.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    info_group.add_argument(
        "--list-modules",
        action="store_true",
        help="List available scan modules and exit",
    )
    info_group.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface (requires GUI to be installed)",
    )

    return parser


def list_modules() -> None:
    print("Available Scan Modules:")
    print()
    modules = [
        ("port", "Check for exposed ports and authentication bypass"),
        ("credential", "Scan for exposed API keys and tokens"),
        ("config", "Validate Clawdbot configuration files"),
        ("process", "Check Clawdbot process security"),
        ("permission", "Validate file permissions"),
        ("network", "Analyze network exposure"),
        ("clawdbot", "Check Clawdbot/Moltbot security configurations"),
    ]

    for name, description in modules:
        print(f"  {name:12} - {description}")
    print()


def print_disclaimer() -> None:
    print("""
+====================================================================+
|                    SECURITY DISCLAIMER                             |
+====================================================================+
|  This tool ONLY scans YOUR local computer.                         |
|  It will NOT access any external systems.                          |
|  All scanning is done locally and safely.                          |
|                                                                    |
|  By using this tool, you agree to only scan systems you own        |
|  or have explicit permission to scan.                              |
+====================================================================+
""")


def launch_gui() -> int:
    """Launch the graphical user interface."""
    import os
    import subprocess

    gui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clawd-for-dummies-gui')

    if not os.path.exists(gui_dir):
        print("Error: GUI is not installed.")
        print("To install the GUI, navigate to the clawd-for-dummies-gui directory")
        print("and run: npm install && npm run electron:dev")
        return 1

    # Check if node_modules exists
    node_modules = os.path.join(gui_dir, 'node_modules')
    if not os.path.exists(node_modules):
        print("GUI dependencies not installed. Installing now...")
        print(f"Running 'npm install' in {gui_dir}...")
        try:
            subprocess.run(['npm', 'install'], cwd=gui_dir, check=True)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return 1
        except FileNotFoundError:
            print("Error: npm is not installed. Please install Node.js to use the GUI.")
            return 1

    print()
    print("Launching GUI application...")
    print()
    print("TIP: Use the View Mode toggle in the header to switch between:")
    print("  - Dev View (CLI-like terminal style)")
    print("  - Friendly View (card-based, user-friendly)")
    print()

    # Try Electron first, fall back to Vite dev server
    try:
        subprocess.run(['npm', 'run', 'electron:dev'], cwd=gui_dir, check=True)
        return 0
    except subprocess.CalledProcessError:
        print("Electron failed, trying web-only mode...")
        try:
            subprocess.run(['npm', 'run', 'dev'], cwd=gui_dir, check=True)
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Error launching GUI: {e}")
            return 1
    except FileNotFoundError:
        print("Error: npm is not installed. Please install Node.js to use the GUI.")
        return 1


def main(args: Optional[list] = None) -> int:
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.list_modules:
        list_modules()
        return 0

    if parsed_args.gui:
        return launch_gui()

    log_level = (
        "DEBUG" if parsed_args.verbose else "WARNING" if parsed_args.silent else "INFO"
    )
    setup_logging(log_level)

    if not parsed_args.silent:
        print_disclaimer()

    if not parsed_args.silent:
        print("Collecting system information...")

    system_info = SystemInfo.collect()

    if not parsed_args.silent:
        print(f"Platform: {system_info.platform_display}")
        print(f"User: {system_info.username}")
        print()

    if parsed_args.modules:
        modules = parsed_args.modules
    elif parsed_args.quick:
        modules = ["port", "config"]
    else:
        modules = [
            "port",
            "credential",
            "config",
            "process",
            "permission",
            "network",
            "clawdbot",
        ]

    scanner = SecurityScanner(
        modules=modules,
        system_info=system_info,
        verbose=parsed_args.verbose,
    )

    if not parsed_args.silent:
        print(f"Running security scan (modules: {', '.join(modules)})...")
        print()

    try:
        scan_result = scanner.run()
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n\nERROR: Scan failed - {e}")
        if parsed_args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    cli = CLI()

    if parsed_args.output == "console":
        output = cli.format_scan_result(scan_result)
        if parsed_args.output_file:
            with open(parsed_args.output_file, "w", encoding="utf-8") as f:
                f.write(output)
            if not parsed_args.silent:
                print(f"\nReport saved to: {parsed_args.output_file}")
        else:
            print(output)
    else:
        from clawd_for_dummies.report_generator import ReportGenerator

        generator = ReportGenerator()

        if parsed_args.output == "html":
            output = generator.generate_html(scan_result)
        elif parsed_args.output == "json":
            output = generator.generate_json(scan_result)
        elif parsed_args.output == "markdown":
            output = generator.generate_markdown(scan_result)
        else:
            output = cli.format_scan_result(scan_result)

        if parsed_args.output_file:
            with open(parsed_args.output_file, "w", encoding="utf-8") as f:
                f.write(output)
            if not parsed_args.silent:
                print(f"\nReport saved to: {parsed_args.output_file}")
        else:
            print(output)

    if scan_result.risk_level.value == "critical":
        return 2
    elif scan_result.risk_level.value == "high":
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
