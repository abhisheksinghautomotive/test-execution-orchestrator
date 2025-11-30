#!/usr/bin/env python3
"""
Enforce security policy based on scan results.

Reads security scan outputs (Bandit, pip-audit, Gitleaks) and enforces
policy thresholds defined in policy.yml, with exceptions from allowlist.yml.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """Load JSON file, return None if not found."""
    path = Path(filepath)
    if not path.exists():
        print(f"WARNING: {filepath} not found, skipping", file=sys.stderr)
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse {filepath}: {e}", file=sys.stderr)
        return None


def load_yaml(filepath: str) -> Optional[Dict[str, Any]]:
    """Load YAML file, return None if not found."""
    path = Path(filepath)
    if not path.exists():
        print(f"WARNING: {filepath} not found, using defaults", file=sys.stderr)
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse {filepath}: {e}", file=sys.stderr)
        return None


def check_bandit(
    report: Optional[Dict[str, Any]],
    policy: Dict[str, Any],
    allowlist: Dict[str, Any],
) -> bool:
    """Check Bandit scan results against policy."""
    if not report:
        return True

    results = report.get("results", [])

    # Count by severity
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    # Get allowlist
    allowed_issues = allowlist.get("bandit", [])

    for issue in results:
        # Check if issue is in allowlist
        is_allowed = False
        for allowed in allowed_issues:
            if allowed.get("id") == issue.get("test_id") and allowed.get(
                "file"
            ) in issue.get("filename", ""):
                print(
                    f"INFO: Bandit issue {issue['test_id']} in {issue['filename']} is allowlisted: {allowed.get('reason')}"
                )
                is_allowed = True
                break

        if not is_allowed:
            severity = issue.get("issue_severity", "UNKNOWN")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

    # Check thresholds
    bandit_policy = policy.get("bandit", {})
    max_high = bandit_policy.get("max_high", 0)
    max_medium = bandit_policy.get("max_medium", 0)
    max_low = bandit_policy.get("max_low", 10)

    print("\nBandit Results:")
    print(f"  HIGH: {severity_counts['HIGH']} (max: {max_high})")
    print(f"  MEDIUM: {severity_counts['MEDIUM']} (max: {max_medium})")
    print(f"  LOW: {severity_counts['LOW']} (max: {max_low})")

    if severity_counts["HIGH"] > max_high:
        print(
            f"ERROR: Bandit HIGH severity issues exceed threshold ({severity_counts['HIGH']} > {max_high})",
            file=sys.stderr,
        )
        return False
    if severity_counts["MEDIUM"] > max_medium:
        print(
            f"ERROR: Bandit MEDIUM severity issues exceed threshold ({severity_counts['MEDIUM']} > {max_medium})",
            file=sys.stderr,
        )
        return False
    if severity_counts["LOW"] > max_low:
        print(
            f"ERROR: Bandit LOW severity issues exceed threshold ({severity_counts['LOW']} > {max_low})",
            file=sys.stderr,
        )
        return False

    print("✓ Bandit checks passed")
    return True


def check_pip_audit(
    report: Optional[Dict[str, Any]],
    policy: Dict[str, Any],
    allowlist: Dict[str, Any],
) -> bool:
    """Check pip-audit results against policy."""
    if not report:
        return True

    vulnerabilities = report.get("vulnerabilities", [])
    if not vulnerabilities:
        print("\n✓ pip-audit: No vulnerabilities found")
        return True

    # Count by severity
    severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    # Get allowlist
    allowed_cves = allowlist.get("pip_audit", [])

    for vuln in vulnerabilities:
        # Check if CVE is in allowlist
        is_allowed = False
        for allowed in allowed_cves:
            if allowed.get("cve") == vuln.get("id"):
                print(
                    f"INFO: CVE {vuln['id']} in {vuln.get('package')} is allowlisted: {allowed.get('reason')}"
                )
                is_allowed = True
                break

        if not is_allowed:
            severity = vuln.get("severity", "UNKNOWN").upper()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

    # Check thresholds
    audit_policy = policy.get("pip_audit", {})
    max_high = audit_policy.get("max_high", 0)
    max_medium = audit_policy.get("max_medium", 0)
    max_low = audit_policy.get("max_low", 10)

    print("\npip-audit Results:")
    print(f"  HIGH: {severity_counts.get('HIGH', 0)} (max: {max_high})")
    print(f"  MEDIUM: {severity_counts.get('MEDIUM', 0)} (max: {max_medium})")
    print(f"  LOW: {severity_counts.get('LOW', 0)} (max: {max_low})")

    if severity_counts.get("HIGH", 0) > max_high:
        print(
            f"ERROR: pip-audit HIGH severity issues exceed threshold ({severity_counts['HIGH']} > {max_high})",
            file=sys.stderr,
        )
        return False
    if severity_counts.get("MEDIUM", 0) > max_medium:
        print(
            f"ERROR: pip-audit MEDIUM severity issues exceed threshold ({severity_counts['MEDIUM']} > {max_medium})",
            file=sys.stderr,
        )
        return False
    if severity_counts.get("LOW", 0) > max_low:
        print(
            f"ERROR: pip-audit LOW severity issues exceed threshold ({severity_counts['LOW']} > {max_low})",
            file=sys.stderr,
        )
        return False

    print("✓ pip-audit checks passed")
    return True


def check_gitleaks(
    report: Optional[Dict[str, Any]],
    policy: Dict[str, Any],
    allowlist: Dict[str, Any],
) -> bool:
    """Check Gitleaks results against policy."""
    if not report:
        return True

    findings: List[Any] = report if isinstance(report, list) else []
    if not findings:
        print("\n✓ Gitleaks: No secrets found")
        return True

    # Get allowlist
    allowed_findings = allowlist.get("gitleaks", [])

    # Filter out allowed findings
    actual_findings = []
    for finding in findings:
        is_allowed = False
        for allowed in allowed_findings:
            if allowed.get("fingerprint") == finding.get("Fingerprint"):
                print(
                    f"INFO: Gitleaks finding {finding.get('Fingerprint')} is allowlisted: {allowed.get('reason')}"
                )
                is_allowed = True
                break
        if not is_allowed:
            actual_findings.append(finding)

    # Check threshold
    gitleaks_policy = policy.get("gitleaks", {})
    max_findings = gitleaks_policy.get("max_findings", 0)

    print("\nGitleaks Results:")
    print(f"  Findings: {len(actual_findings)} (max: {max_findings})")

    if len(actual_findings) > max_findings:
        print(
            f"ERROR: Gitleaks findings exceed threshold ({len(actual_findings)} > {max_findings})",
            file=sys.stderr,
        )
        for finding in actual_findings:
            print(
                f"  - {finding.get('Description')} in {finding.get('File')}",
                file=sys.stderr,
            )
        return False

    print("✓ Gitleaks checks passed")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Enforce security policy based on scan results"
    )
    parser.add_argument("--bandit", help="Path to Bandit JSON report")
    parser.add_argument("--pip-audit", help="Path to pip-audit JSON report")
    parser.add_argument("--gitleaks", help="Path to Gitleaks JSON report")
    parser.add_argument(
        "--policy", required=True, help="Path to policy.yml configuration"
    )
    parser.add_argument(
        "--allowlist", required=True, help="Path to allowlist.yml configuration"
    )

    args = parser.parse_args()

    # Load configurations
    policy = load_yaml(args.policy) or {}
    allowlist = load_yaml(args.allowlist) or {}

    # Load reports
    bandit_report = load_json(args.bandit) if args.bandit else None
    audit_report = load_json(args.pip_audit) if args.pip_audit else None
    gitleaks_report = load_json(args.gitleaks) if args.gitleaks else None

    # Run checks
    passed = True
    passed &= check_bandit(bandit_report, policy, allowlist)
    passed &= check_pip_audit(audit_report, policy, allowlist)
    passed &= check_gitleaks(gitleaks_report, policy, allowlist)

    if passed:
        print("\n✅ All security policy checks passed")
        sys.exit(0)
    else:
        print("\n❌ Security policy checks failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
