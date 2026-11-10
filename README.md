# Vivaldi — The Four Seasons | Ars Sonora

An online music gallery built with React, Three.js and Blender. The complete reference catalog contains 20 local MP3 recordings (approximately 98 minutes): 12 movements of the four concertos, plus 8 additional interpretations.

## Local preview

```sh
npm install
npm run dev
```

Open http://127.0.0.1:5174/. Requires Node.js 22.18+ or 24+. This workspace reuses previously installed dependencies via a local node_modules symlink; a clean lockfile is included for an independent install. This site has not been published or deployed.

## The expanded museum

The model has a 22 × 64 metre floor (1,408 m²), four sequential season galleries, twelve dedicated movement paintings, five historical portrait displays, four interpretation desks and an entrance shop. It has more than twice the previous gallery's modeled floor area. The interpretation desks accommodate the additional versions in each season: Spring 2, Summer 3, Autumn 1, Winter 2.

Walk with WASD or arrow keys, hold Shift for speed, drag to look, or hold the on-screen direction controls on mobile. Gallery navigation provides direct arrivals. Walls, the instrument plinth, benches, shop and interpretation desks have collision footprints.

Click a seasonal painting to play its movement. Each season panel lists the three main movements and opens the full season catalog. The collection supports season filtering, search, per-recording download, local personal audio, playback, seek, volume, shuffle and repeat.

## Recording rights

Tracks 01–12: John Harrison, Robert Turizziani and The Wichita State University Chamber Players, CC BY-SA 4.0. Tracks 13–20: Gregor Quendel, CC BY-NC 4.0. The latter recordings are for noncommercial use under their stated license. The fictional shop never collects money. Full source links, credits, license links and an unchanged-file manifest are in CREDITS.md and public/audio/vivaldi/.

## Editable assets

- blender/Vivaldi-Four-Seasons-Museum.blend: editable master scene.
- blender/Vivaldi-Four-Seasons-Web.blend: baked web variant.
- blender/vivaldi-museum-preview.png: Cycles architectural render.
- public/models/vivaldi-four-seasons.glb: compressed web model.
- src/catalog.json: all 20 recordings and season metadata.
- src/layout.json: shared physical dimensions, arrivals and painting locations, used by Blender and frontend navigation.

Rebuild in this order with the installed Blender application:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python blender/build_vivaldi.py -- --render-preview
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python blender/bake_vivaldi.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python blender/denoise_vivaldi.py
```

The builder uses the original project modeling utilities in build_museum.py. Paintings and portraits retain their original UVs; architecture uses a Cycles lighting atlas cleaned in Blender's compositor. Metallic framing retains PBR highlights. A subtle floor reflection is rendered in Three.js. Browser output and the Cycles reference use different render pipelines and are not pixel-identical.

## Verification

```sh
npm run lint
npm run typecheck
npm test
npm run build
```

Twelve tests check cart pricing/removal, all audio files and licenses, the full catalog, season grouping, physical capacity, safe arrival points, WASD heading, diagonal speed, Shift, bounds, collision and frame-time limits. Static output is in dist/. Audio is not preloaded; 3D is loaded separately with progress feedback. Rendering resolution, reflections and shadows are capped on mobile. Rendering pauses when the scene is unchanged.
