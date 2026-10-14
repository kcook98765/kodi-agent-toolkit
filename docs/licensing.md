# Licensing and attribution

## Toolkit source

The existing [MIT license](../LICENSE) is retained unchanged for original toolkit code, portable skills, references, fixtures, generated icons, and community policy. Dependencies are installed separately; their software and license texts are not bundled or relicensed by this repository. GitHub's generated source archive is the intended release artifact; no wheels, venvs, Kodi packages, or metadata cache are attached.

## Kodi ecosystem references

| Material | Relationship and license boundary |
|---|---|
| [Kodistubs](https://github.com/romanvm/Kodistubs) 20.0.1 | Installed static development dependency, not a runtime Kodi implementation. Pinned [license](https://github.com/romanvm/Kodistubs/blob/5a7c9c13e8a1cc368a2e91cbbe91d4d8fd211090/LICENSE.txt): GPL-3.0-only in the dependency inventory. No stub bodies copied into toolkit source. |
| Official [addon-check](https://github.com/xbmc/addon-check) / kodi-addon-checker 0.0.36 | Called through the independently installed checker entry point. Pinned [SPDX license](https://github.com/xbmc/addon-check/blob/67be5c1eca23e01402a447f995e2216bd83202f3/LICENSES/GPL-3.0-only): GPL-3.0-only. Its package also carries third-party notices; preserve those when redistributing it. No checker source vendored. |
| [KodiAI](https://github.com/xbmc/kodiai/tree/545b9afa96695f7c97bf0e2ab214295ba45dd196) | Research reference for general contextual review concepts. Its pinned [license](https://github.com/xbmc/kodiai/blob/545b9afa96695f7c97bf0e2ab214295ba45dd196/LICENSE) is proprietary; this toolkit includes no copied code, prompts, fallback text, or proprietary rule prose. The local review contract and evidence helpers are original. |
| [Kodi Wiki](https://kodi.wiki/view/Addon.xml) and tagged Kodi API sources | Linked policy/API facts and independent concise guidance; no reproduced manuals. Kodi Wiki carries CC BY-SA 3.0. Review the source-specific terms before copying expressive documentation or source. |
| [OpenCode](https://github.com/anomalyco/opencode) / @opencode-ai/plugin | Optional reference agent/SDK, MIT. Installed separately for adapters/model evaluation, absent from standalone Python installation. |
| [Kodi Lab](https://github.com/kcook98765/kodi-lab) | Separate optional runtime project, not bundled or modified by the toolkit. Follow its own installation and licensing. |

When redistributing GPL components or a combined distribution, review the GPL's notices, license-copy and corresponding-source requirements for that distribution. This repository's MIT license grants no exception. Redistribution of dependency wheels, copied stub/checker code, packaged runtimes, or a combined product is outside this source-only beta assessment. No conclusion here certifies the licensing of an arbitrary downstream combination.

## Locked development dependencies

The following versions/licenses match the lock and installed distribution metadata reviewed for the beta. Full upstream URLs and hash counts are in [dependency-inventory.json](dependency-inventory.json); requirements-dev.lock contains the accepted wheel hashes. These are license identifiers, not replacement license notices for a redistributed dependency bundle.

| Distribution | Pinned version | License |
|---|---|---|
| [ast_serialize](https://github.com/mypyc/ast_serialize) | 0.13.0 | MIT |
| [certifi](https://github.com/certifi/python-certifi) | 2026.7.22 | MPL-2.0 |
| [charset-normalizer](https://github.com/jawah/charset_normalizer/blob/master/CHANGELOG.md) | 3.5.2 | MIT |
| [colorama](https://github.com/tartley/colorama) | 0.4.6 | BSD-3-Clause |
| [elementpath](https://github.com/sissaschool/elementpath) | 5.1.4 | MIT |
| [idna](https://github.com/kjd/idna) | 3.20 | BSD-3-Clause |
| [kodi-addon-checker](https://github.com/xbmc/addon-check) | 0.0.36 | GPL-3.0-only |
| [Kodistubs](https://github.com/romanvm/Kodistubs) | 20.0.1 | GPL-3.0-only |
| [librt](https://github.com/mypyc/librt) | 0.16.0 | MIT |
| [mando](https://mando.readthedocs.org/) | 0.7.1 | MIT |
| [mypy](https://www.mypy-lang.org/) | 2.4.0 | MIT |
| [mypy_extensions](https://github.com/python/mypy_extensions) | 1.1.0 | MIT |
| [packaging](https://github.com/pypa/packaging) | 26.3 | Apache-2.0 OR BSD-2-Clause |
| [pathspec](https://python-path-specification.readthedocs.io/en/latest/changes.html) | 1.1.1 | MPL-2.0 |
| [pillow](https://python-pillow.github.io) | 12.3.0 | MIT-CMU |
| [polib](https://github.com/izimobil/polib/) | 1.2.0 | MIT |
| [radon](https://radon.readthedocs.org/) | 6.0.1 | MIT |
| [requests](https://github.com/psf/requests) | 2.34.2 | Apache-2.0 |
| [setuptools](https://github.com/pypa/setuptools) | 84.0.0 | MIT |
| [six](https://github.com/benjaminp/six) | 1.17.0 | MIT |
| [typing_extensions](https://github.com/python/typing_extensions/issues) | 4.16.0 | PSF-2.0 |
| [urllib3](https://github.com/urllib3/urllib3/blob/main/CHANGES.rst) | 2.8.0 | MIT |
| [wheel](https://github.com/pypa/wheel) | 0.48.0 | MIT |
| [xmlschema](https://github.com/sissaschool/xmlschema) | 4.3.2 | MIT |

## Publication review

Only original source, safe fixtures, original helpers, documentation, examples and sanitized numeric evaluation evidence are published. Raw transcripts, private credential/configuration files, Kodi library metadata, runtime diagnostics, dependency packages, generated caches and Kodi binaries are excluded. All included PNG paths share one original generated fixture image. Phase 7's report records the candidate/history scan boundary and the separate initial-snapshot decision.
