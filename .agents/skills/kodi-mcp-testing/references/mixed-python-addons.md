# Mixed Python add-ons

Keep the intended manifest extensions and verify their declared libraries. A script, plugin and service can coexist in one add-on. Structure and native installation are separate from whether a particular entry can be explicitly launched. Kodi owns the service lifecycle. Never launch a service library as a script.

Install an admitted package through one managed native installation intent. Native dependencies can contain multiple legitimate extensions. For packages declaring services, use the optional `allow_services` intent only with explicit authorization. The launch operation supports a qualified script or plugin entry. When multiple native behaviors are present, inspect the resulting UI, logs or normal Kodi service behavior separately.

The official checker and the release-matched static type stage remain useful for manifest paths and Python API use. `xbmc.service` timing metadata such as `start="login"` is not a file path. Preserve warnings and runtime limits.
