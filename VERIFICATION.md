# Verification — Vivaldi: The Four Seasons

Verified locally on 10 November 2026. This is a local preview; no commit, push or deployment was made.

## Build and assets

- `npm run lint`: passed.
- `npm run typecheck`: passed.
- `npm test`: 12 passed, 0 failed. Coverage includes commerce totals, walking and collision rules, season arrivals, the 20-recording catalogue, local MP3 signatures and attribution, and the final model's exhibit metadata.
- `npm run build`: passed. The final distribution contains all 20 MP3s. Its GLB checksum matches the final public model.
- Blender 5.2.3 generated the enlarged editable museum, rendered its architectural preview, baked a 6144×6144 Cycles diffuse lighting atlas, denoised it and exported the Meshopt model.
- The museum occupies 22×64 m (1,408 m²), more than twice the preceding 18×33 m layout. Its model metadata declares four season galleries, 20-recording capacity, 12 movement paintings and four interpretation stations.
- The catalogue contains 12 main movements plus eight additional interpretations, about 98 minutes in total. Per-season totals are Spring 5, Summer 6, Autumn 4 and Winter 5. Original audio files remain unmodified, with SHA-256 checksums and source credits.
- Performance tradeoff: the separately loaded Three.js chunk is about 158 kB gzip and the final GLB is 17.87 MiB. Progress feedback is provided while the model loads. Audio uses `preload="none"`; all 123 MiB of music is not fetched on entry. Load time will depend on connection speed; no field performance score is claimed.

## Browser checks

Checked desktop 1440×900, tablet 1024×768 and 768×1024, and phone 390×844. Document width matched the viewport at each size. The phone collection dialog also had no horizontal overflow. The final QA tab recorded no console errors or warnings.

All four season navigation stops showed their three primary movements and correct complete-recording counts. Search, season filters, individual download links and the empty-search recovery action were checked. A Spring MP3 was downloaded through the browser successfully.

Audio was observed playing from local MP3s: Spring I, Spring II, Winter II and the additional Summer piano interpretation. Clicking the actual Spring II wall painting selected `/audio/vivaldi/02.mp3` and started playback. Pausing worked. The earlier player validation also covered seeking, mute and local-file playback from a `blob:` URL.

Actual held-key WASD was tested in the far Winter gallery: holding W changed the camera from `0.000,1.720,-18.000` to `-0.949,1.720,-19.518` and entered free-walk mode. On phone, holding the visible forward control changed the camera from `-0.000,2.150,31.000` to `-0.000,1.720,29.245` and entered free-walk mode. Unit checks cover diagonal normalization, faster Shift movement, frame-delta limits, museum boundaries and obstacle collisions.

The Vivaldi tote was added to the phone basket and checked out for a simulated Rp145,000. Checkout showed a disabled processing state, then a successful demo order; the basket returned to zero. No payment or personal information was required. The earlier commerce validation also checked quantity changes and removal.

Native dialog focus trapping and Escape dismissal were checked. Controls have labels, focus styling and visible instructions. Movement controls support pointer hold and keyboard Enter/Space. Text inputs, sliders and open dialogs suppress walking keys. Reduced motion disables camera travel interpolation and CSS transitions. WebGL failure and invalid-file recovery are implemented; these failures were not forcibly induced in this final pass.

## Review and evidence

Reviewed the source changes, local asset manifest, licence distinctions, credits and model exhibit metadata. No old Leonardo artwork remains in the active Vivaldi interface. The workspace has no Git repository or baseline diff; source and generated assets were reviewed directly as a new local project.

Screenshots in the parent `outputs/` directory: `vivaldi-gallery-desktop.jpg`, `vivaldi-spring-desktop.jpg`, `vivaldi-gallery-mobile.jpg` and `vivaldi-collection-mobile.jpg`. The editable Blender master, baked derivative and Cycles preview are in this project's `blender/` directory.
