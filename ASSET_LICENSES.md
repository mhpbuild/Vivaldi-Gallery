# License scope and asset permissions

The root MIT LICENSE covers original software, tests, Blender Python scripts, configuration and documentation. It does **not** relicense third-party recordings, portraits, fonts or dependency code. This is a collection of independently licensed works, not an MIT license grant over every file.

## Original project media

© 2026 mhpbuild and contributors. Original project modeling, procedural textures, renders, screenshots, the parchment illustration and four seasonal image atlases are offered under [CC BY 4.0](licenses/CC-BY-4.0.txt), to the extent copyright or similar rights are held by the contributors. Attribute “Vivaldi Gallery — mhpbuild”, link to this repository and the license, and indicate your changes. No exclusive copyright is asserted over AI-generated elements that are not eligible for copyright.

This covers the project's original contributions in:

- `blender/Vivaldi-Four-Seasons-*.blend` and `blender/vivaldi-museum-preview.png`;
- `public/models/vivaldi-four-seasons.glb`;
- `public/art/vivaldi-{spring,summer,autumn,winter}.png` and `public/art/parchment.png`;
- `public/textures/` and `docs/images/`.

Historical portrait reproductions embedded in a model or screenshot retain their public-domain status. Original geometry and illustrations do not claim authenticity, historical provenance or endorsement. AI assistance was used for programming and new illustrations. Microsoft/system fonts are not bundled; master scenes reference external fonts, and the exported GLB contains text geometry rather than font files.

## Audio: original rights remain with the musicians

| Files | Creator / performance | License |
| --- | --- | --- |
| `public/audio/vivaldi/01.mp3`–`12.mp3` | John Harrison, Robert Turizziani, Wichita State University Chamber Players | [CC BY-SA 4.0](licenses/CC-BY-SA-4.0.txt) |
| `public/audio/vivaldi/13.mp3`–`20.mp3` | Gregor Quendel; arrangement credits in CREDITS.md | [CC BY-NC 4.0](licenses/CC-BY-NC-4.0.txt) |

Source and the original download URLs are in [CREDITS.md](CREDITS.md), the browser's credits panel and `src/catalog.json`. Files are unchanged copies; `public/audio/vivaldi/checksums.json` records their SHA-256 hashes. Keep the music credits and license notices with redistributed copies. The BY-SA terms govern adaptations of that licensed material; the BY-NC files may not be used commercially without separate permission. The prototype is noncommercial, has no paid checkout and does not sell or sublicense recordings.

When embedding or adapting music into another work, review the applicable full license. The MIT license for this app is not a substitute for the relevant music license.

## Historical portraits

`public/art/vivaldi-engraving.jpg` (François Morellon de La Cave, 1725) and `public/art/vivaldi-portrait.jpg` (anonymous, traditionally associated with Vivaldi) are public-domain reproductions from Wikimedia Commons. See the source records in [CREDITS.md](CREDITS.md). The oil portrait's identification is debated. No new exclusive rights are asserted over these reproductions.

## Dependencies, fonts and earlier experiments

Dependencies retain their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This repository's original commit remains in history. Removed prototype assets remain discoverable there and keep the licenses and attribution documented in the history section of that notice. Removing them from the current tree does not erase them from Git history.
