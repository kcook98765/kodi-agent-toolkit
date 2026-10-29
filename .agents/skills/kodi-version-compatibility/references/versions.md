# Dependency interpretation

An `<import version>` declares a minimum dependency version. A higher provided version may satisfy that dependency; the field is not a maximum Kodi release. Do not infer that 3.0.0 excludes Omega/Piers, or that meeting the dependency proves the source works on every release. Confirm actual source APIs, target and matching stubs. See [official addon.xml dependency semantics](https://kodi.wiki/view/Addon.xml#version_attribute).

## Verified compatibility evidence (2026-10-13)
| Kodi | Evidence snapshot | xbmc.python API / ABI | Published matching stubs |
|---|---|---|---|
| 19 Matrix | 19.5, released | 3.0.0 / 3.0.0 | 19.0.3 |
| 20 Nexus | 20.5, released | 3.0.1 / 3.0.0 | 20.0.1 (tested toolkit environment) |
| 21 Omega | 21.3, released | 3.0.1 / 3.0.0 | 21.0.0 (available, not installed here) |
| 22 Piers | 22.0rc1, prerelease | 3.1.0 / 3.0.0 | no PyPI 22 release verified |
Kodistubs source declares 22.0.0a3 but is not a published matching distribution. No complete stub coverage or all-platform compatibility is claimed. API dependency values are not CPython versions.

This is a dated reference snapshot, not a current package/release lookup or a multi-version qualification matrix. Preserve the pinned Nexus checker/stub lane unless a separate measured change qualifies another environment. Selecting a different CLI checker branch does not replace the installed stubs. Matrix, Nexus, Omega and Kodi 22 preview each need matching API/type/checker evidence and their own recorded runtime behavior; passing one lane never qualifies another. Kodi Lab's runtime catalog, stored Bridge trust or saved native acceptance cannot fill an unexecuted toolkit/add-on check.

Concrete boundaries: xbmcvfs.translatePath exists across 19-22; deprecated xbmc.translatePath in 19 is removed from 20+. getVideoInfoTag exists in 19, but modern setters such as InfoTagVideo.setTitle and Addon.getSettings are 20+; setVideoAssetTitle is 21+. ListItem.setInfo is retained with partial deprecation, not wholly removed. Selected ListItem setters and HDR details are 22 prerelease additions. Check each signature rather than extending one fact to every method.
The historical toolkit pilot qualified only a disposable 20.5 runtime. This is not a prerequisite or claim about the current user's environment. A Python 3.12 type check is not proof of the target's interpreter. Current master API docs identify moving 23 development; use tagged evidence for version claims.
Pinned manifests:
- https://github.com/xbmc/xbmc/blob/f8fdeb6b1b1a7b753e1559d34a98cea62b4920d9/addons/xbmc.python/addon.xml
- https://github.com/xbmc/xbmc/blob/4b95737efaddf7c869736e539318f18433413ff1/addons/xbmc.python/addon.xml
- https://github.com/xbmc/xbmc/blob/a3a448d26b8d560a65655dab2cd122994dc4e146/addons/xbmc.python/addon.xml
- https://github.com/xbmc/xbmc/blob/28ea2eac1eb7af8fdcbd2672d933ce87f594be79/addons/xbmc.python/addon.xml
Initial-release API declarations: https://github.com/xbmc/xbmc/tree/f44fdfbf675f30c01e7639177a34544e6a6b9dad/xbmc/interfaces/legacy ; https://github.com/xbmc/xbmc/tree/389e701cb96e5543c303c4004811b51684d67dd4/xbmc/interfaces/legacy ; https://github.com/xbmc/xbmc/tree/60c450005472e6d38929bb28c07d00589102818d/xbmc/interfaces/legacy
22 RC evidence: https://kodi.tv/article/kodi-22-piers-rc-1/
