# Third-party notices

## Current music and portraits

Full artist, source, license and per-track notices are in [CREDITS.md](CREDITS.md), [ASSET_LICENSES.md](ASSET_LICENSES.md), and `public/audio/vivaldi/CREDITS.txt`. Full Creative Commons license texts are in `licenses/`. Classicals.de and the credited musicians do not endorse this project.

## Software dependencies

The following are used as dependencies, not copied into this repository's source tree. Their original notices and license files are installed with their npm packages. Preserve those notices when redistributing their code or a bundle containing it.

| Dependency | License / source |
| --- | --- |
| React and React DOM | MIT · https://github.com/facebook/react |
| Three.js and the used GLTF/Meshopt loader helpers | MIT · https://github.com/mrdoob/three.js |
| Lucide React icons | ISC · https://github.com/lucide-icons/lucide |
| Vite and its React plugin | MIT · https://github.com/vitejs/vite |
| TypeScript | Apache-2.0 · https://github.com/microsoft/TypeScript |
| ESLint | MIT · https://github.com/eslint/eslint |
| typescript-eslint | MIT · https://github.com/typescript-eslint/typescript-eslint |
| DefinitelyTyped type definitions | MIT · https://github.com/DefinitelyTyped/DefinitelyTyped |

The exact direct and transitive dependency versions are recorded in `package-lock.json`. Refer to each installed package's license for the authoritative terms. A third-party dependency's license is not replaced by this project's MIT license.

## Fonts

Cinzel, Cormorant Garamond, DM Sans and Instrument Serif are requested from Google Fonts. Their Google Fonts families use the SIL Open Font License 1.1; see the family repositories at https://github.com/google/fonts/tree/main/ofl. No font binaries are checked in here. The Blender master references a locally available Times New Roman font; that proprietary font file is not packed or redistributed. The builder falls back to Blender's built-in font when the system font is unavailable.

## Earlier prototype assets retained in Git history

The first commit included three unrelated music demos. They have been removed from the active Vivaldi gallery and current public tree, but remain available in the initial commit. These notices continue to apply to those copies:

| Historical path | Credit | Source and identifier |
| --- | --- | --- |
| `public/audio/dream-culture.mp3` | “Dream Culture” — Kevin MacLeod (incompetech.com) | https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1300046 |
| `public/audio/floating-cities.mp3` | “Floating Cities” — Kevin MacLeod (incompetech.com) | https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1600018 |
| `public/audio/local-forecast.mp3` | “Local Forecast” — Kevin MacLeod (incompetech.com) | https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1300010 |

These unedited audio copies are licensed under **Creative Commons Attribution 4.0 International**: https://creativecommons.org/licenses/by/4.0/. See also https://incompetech.com/music/royalty-free/licenses/. The descriptive filenames differ from the source filenames; the audio was not edited. The earlier MIT/source release does not grant ownership of these recordings.

Older Ars Sonora Blender scenes, the old GLB, lighting maps, renders, `renaissance-music-triptych.png`, and the parchment previously named `leonardo-parchment.png` are original project experiments. The illustrations were generated with AI, not taken from Leonardo da Vinci or another historical artist. The original project contributions in those assets are offered under CC BY 4.0, to the extent rights are held by contributors. No font binaries were packed in those Blender scenes. They are retained in history for provenance, not presented as part of the active Vivaldi catalogue.
