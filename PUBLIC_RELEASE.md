# Public release review — 10 November 2026

## Scope

Vivaldi-Gallery is an independent, noncommercial fan project. The public README states the programmer's appreciation for Vivaldi, peaceful intent, absence of affiliation or endorsement, and simulated nature of the shop. The project code is MIT; media is explicitly excluded from that blanket grant and covered by per-asset notices.

## Curated current tree

- Included: original app and tests, four-season layout and catalogue, twenty attributed recordings, public-domain portraits, original AI-assisted illustrations, current Blender scenes, web GLB, current lighting textures, build scripts and source documentation.
- Removed from the current tree: ten inactive prototype outputs (the old Ars Sonora scenes/model/render/lighting, the unrelated triptych and three Kevin MacLeod demos). Copies were preserved outside this Git repository for local archival use.
- Renamed the existing parchment asset to a neutral filename and updated its runtime reference. The image itself was not edited.
- Excluded: installed dependencies, build output, Vite cache, environment files, editor settings, logs, Blender backup files and archive packages.
- Kept package-lock.json and Node 24 CI. The npm package remains private to prevent accidental npm publication; this does not determine GitHub repository visibility.

## Rights and provenance

Classicals.de's specific Four Seasons page was checked against its licensing page on 10 November 2026: main twelve recordings use CC BY-SA 4.0; eight additional recordings use CC BY-NC 4.0. The audio remains unmodified. Wikimedia portrait source records and Google Fonts license files were checked. Full Creative Commons license texts are bundled from creativecommons.org. Software dependency metadata was inspected; its own notices remain applicable.

All four original Blender scenes were inspected in Blender before publication: their images were packed, system-font files were not packed, there were no embedded text/script blocks and no external .blend libraries. The GLB JSON contains no external image or buffer URIs and no local filesystem path markers.

## History and Git transport

The original commit is retained, including normal Git author metadata. The removed media therefore remains reachable in history; THIRD_PARTY_NOTICES.md preserves the historical music and original-asset credits. This release does not claim to purge history. A credential-pattern check across all 78 unique historical blobs found no token or private-key matches; this is a bounded pattern check, not a guarantee that every possible sensitive value can be detected.

The release is delivered as a normal descendant commit and `git push origin main`. Local mirror mode is explicitly false. No force push, mirror push, repository replacement or website deployment is part of this release. New local commits use the GitHub noreply author address; the earlier commit is not rewritten.

## Validation

- Lint, typecheck, all 12 existing tests, and production build passed after curation.
- All 20 original recording hashes match the checked-in manifest. The Vivaldi GLB and both current Blender scenes are byte-for-byte unchanged.
- Local Markdown targets and runtime asset references resolve. The root credits and bundled audio credit sidecar match.
- Browser smoke checks at 1280×720 and 390×844 showed the complete museum and renamed parchment texture, no horizontal overflow, and no new warning/error logs in the fresh QA tab.
- Prior interaction and accessibility checks remain documented in VERIFICATION.md. The separately loaded Three.js bundle still triggers Vite's size advisory; the README describes the model's loading cost.

See README.md, ASSET_LICENSES.md, CREDITS.md and THIRD_PARTY_NOTICES.md for the release-facing notices. The live GitHub CI run provides the independent clean-install check for the release commit.
