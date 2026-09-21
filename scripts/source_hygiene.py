"""Small, offline publication checks. Never print a matched credential value."""
import re

# Deliberately specific signatures, not a claim to detect every possible secret.
SECRET_PATTERNS = {
    'private-key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'github-token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b'),
    'openai-token': re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b'),
    'aws-access-id': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'google-api-key': re.compile(rb'\bAIza[A-Za-z0-9_-]{35}\b'),
    'slack-token': re.compile(rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b'),
}
PERSONAL_PATH = re.compile(rb'(?:[A-Za-z]:[/\\]+Users[/\\]+[^/\\\s\"\'<>]+|<LOCAL_USER>/\s\"\'<>]+|<LOCAL_USER>/\s\"\'<>]+)')
PRIVATE_NAMES = {'.env', '.env.local', '.env.production', 'credentials.json',
                 'id_rsa', 'id_ed25519'}


def secret_findings(data):
    return [{'rule': rule, 'line': data.count(b'\n', 0, match.start()) + 1}
            for rule, pattern in SECRET_PATTERNS.items()
            for match in pattern.finditer(data)]


def personal_path_lines(data):
    return sorted({data.count(b'\n', 0, match.start()) + 1
                   for match in PERSONAL_PATH.finditer(data)})
