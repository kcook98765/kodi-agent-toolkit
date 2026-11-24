# Agent roles

- **kodi-develop** works on local source and static validation. It needs no Kodi Lab connection.
- **kodi-managed-lab** is the opt-in developer for disposable managed profiles. The configured credential needs Trusted Managed Lab authority. Use the shared lease and your own source and snapshots.
- **kodi-inspect** and **kodi-support** inspect separately authorized external targets. Support uses structured diagnostics and logs. Enable screenshots for inspection only when needed.
- **kodi-external-develop** is for registered development targets with explicit deployment, execution or navigation grants. Grant and select the external target separately from managed development.

A client's tool allowlist narrows its actions. The Lab independently enforces the credential's grants, target class and managed owner.
