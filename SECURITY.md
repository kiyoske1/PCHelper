# Security

## Scope

PC Helper is a local Windows utility. It can inspect processes, remove eligible temporary files, flush DNS, and launch built-in Windows tools.

## Reporting a vulnerability

Please do not publish security-sensitive details in a public issue.

Open a private security report through GitHub's repository security reporting features when available. Include:

- affected version
- Windows version
- clear reproduction steps
- expected and actual behavior
- screenshots or logs when useful

Do not include passwords, tokens, personal files, or other private data.

## Safety principles

PC Helper intentionally:

- keeps network diagnostics user-triggered
- avoids deleting recent temporary files
- requires explicit confirmation before cleanup and process termination
- protects core process IDs and its own process
- does not collect telemetry
