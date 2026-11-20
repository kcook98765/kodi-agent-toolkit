# Mixed Python add-ons

Kodi Lab [#394 contract at3d1d459](https://github.com/kcook98765/kodi-lab/blob/3d1d4594a0f10d39fbeab6aa2829a691761922cc/docs/MIXED-PYTHON-ADDONS.md) supports common Python combinations on Matrix19.4, Nexus20.5, Omega21.3 and Piers22RC2. Verify the installed Web/broker and authenticated schemas first. Source support does not prove installation, native application behavior or repeat-start reliability.

A manifest may have a script, a plugin, a service, or a supported combination. Static validation/discovery does not require exactly one functional extension. Each declared library/asset must still be safe and present. Legacy `xbmc.service start="login"` is timing metadata, not a file or launch entry; other extensions' file-valued `start` attributes remain checked. The official checker may report separate deprecated/invalid metadata. Do not alter an add-on to suppress a faulty validator.

For Lab automatic activation the qualified shape is at most one each of `xbmc.python.script`, `xbmc.python.pluginsource` and `xbmc.service`, safe relative present Python libraries and no platform-library overrides. Complete descriptor/tree proof, dependencies, native primary-type identity and current target/workspace/generation/credential checks still apply. Broader descriptors may be valid intake with ineligible activation or launch; fixed-video smoke refusal or one ineligible ordinal does not make the whole add-on invalid.

## Service-bearing sources

Private `project_import` can retain the complete mixed manifest, but private service deployment refuses `project_service_activation_requires_consent` before attachment/copy/restart. Import/editing grants no background-service consent. Use the registered-source path for this lane:

1. Review/register the complete source, create/capture its workspace and validate the exact generation. On a retained profile, inspect identity preview and select the intended target/workspace before attachment/copy.
2. Attach and perform the supported stopped baseline copy. Start Kodi explicitly when authorized and wait for normal native readiness.
3. The authorized administrator explicitly selects **Allow this service to start now and on future Kodi starts while enabled** and **Enable service**. The supported Web request is `POST /api/instances/{target}/development-sources/{source}/enable` with `{"allow_service_start": true}`. This is not an MCP service-enable capability. Inspect enabled inventory separately.
4. Deploy the exact validated workspace generation with `workspace_deploy` in `direct` mode. Preserve operation/tree receipts and reconcile uncertainty under the original identity before a new request.
5. Launch only an eligible script/plugin ordinal from validation's `launch_entries`, through an exposed authorized `development_launch` or `workspace_launch`. Ordinals follow complete manifest order, including non-launchable service declarations. Services are never invoked as scripts: Kodi enable/start/stop lifecycle owns them.
6. Observe fresh script/plugin output/UI and actual timed background service work independently. Enabled state and accepted dispatch do not prove execution. Supported Stop/Start plus evidence of reconstructed persisted work qualify restart behavior; one-running and human-priority protections still apply.

Script+plugin without a service can use its existing private owned-project first-enable route. Single-content video/audio/image/executable plugins have distinct launch destinations; multi-content or repeated executable declarations can be ineligible without invalidating structural intake. Library-path RunScript does not guarantee implicit `xbmcaddon.Addon()` context; verify application-specific explicit-ID use and actual behavior.

An old registered-source baseline can correctly refuse after a later workspace edit/deployment. Do not adopt changed bytes or strip extensions to bypass it. Continue the current exact deployment contract, or deliberately establish a new reviewed stopped baseline when first enablement is required. Preserve failed-start evidence and reconcile uncertain operations. A separately authorized second explicit Start may be used after a terminal first failure; never implement automatic blind retries or report persistent failures as readiness.
