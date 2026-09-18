"""SSRF guard + log redaction for GitHub API requests."""

from __future__ import annotations

import re
import urllib.parse

ALLOWED_GITHUB_API_HOSTS = frozenset({"api.github.com"})
_AUTH_HEADER_RE = re.compile(
    r"(?i)(authorization\s*[:=]\s*['\"]?)(bearer\s+)?(\S+)"
)


class UnsafeGitHubUrlError(ValueError):
    """URL is not an allowlisted GitHub API endpoint."""


def assert_github_api_url(url: str) -> urllib.parse.ParseResult:
    """Require ``https://api.github.com/...`` (no user-controlled hosts)."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise UnsafeGitHubUrlError(f"refusing non-HTTPS URL: {redact_url(url)}")
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_GITHUB_API_HOSTS:
        raise UnsafeGitHubUrlError(
            f"refusing non-allowlisted host {host!r}: {redact_url(url)}"
        )
    if parsed.username or parsed.password:
        raise UnsafeGitHubUrlError("refusing URL with embedded credentials")
    return parsed


def redact_url(url: str) -> str:
    """Strip query/fragment for safer error messages."""
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, "", "", "")
    )


def redact_secrets(text: str) -> str:
    """Redact Authorization bearer tokens from debug / error strings."""
    return _AUTH_HEADER_RE.sub(r"\1\2[REDACTED]", text)
