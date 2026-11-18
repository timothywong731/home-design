---
name: threejs-walkthrough-viewer
description: Use when building or changing the three.js viewer published on GitHub Pages - loading the GLB (meshopt/KTX2), baked lightmaps, first-person and orbit controls, and the 2D floor plan minimap that maps to the 3D scene and shows the viewer's position and look direction (with click-to-teleport and room detection).
---

# three.js walkthrough viewer with linked 2D plan

Files: `plan.mjs` (pure plan<->3D mapping + canvas drawing; node-tested with `node plan.test.mjs`), `viewer.example.js` (full reference wiring; syntax-checked, NOT browser-tested), `plan.test.mjs`.

## The 3D <-> 2D mapping (the important bit)
- One source: `house.json` (`rooms[].polygon`, `walls[]`, `bounds`, `spawn`, Blender metres; see blender-arch-modelling). The plan and the 3D shell cannot drift because both are generated from it.
- Blender (x, y, z) -> glTF/three `(x, z, -y)` (verified on a 5.1.1 export). So plan point `(bx, by) = (three.x, -three.z)`; walking into the house (+Y) = three -Z.
- Plan canvas: +X right, +Y *up* the screen (entrance at the bottom). `makeMap(bounds, w, h).toCanvas/toWorld` handle scale, centring and the y flip.
- **Viewer marker**: position `threeToPlan(camera.position)`; heading `canvasHeading(camera.getWorldDirection(v))` = `atan2(dir.z, dir.x)` (canvas y flips by = -dz twice). FOV cone: horizontal FOV `hfov(camera.fov, camera.aspect)`, drawn as an arc sector of radius ~2.5 m around the heading. Redraw every frame (cheap) or on camera change.
- **Click-to-teleport**: `toWorld(canvasX, canvasY)` -> `planToThree(bx, by, 1.6)`; scale pointer coords by `canvas.width / rect.width` for CSS-scaled canvases/hi-dpi.
- **Room detection**: `pointInPoly(bx, by, room.polygon)` -> highlight room on plan and show its name; also use it to switch lightmap/exposure per room if needed.
- Optional: draw door swings/openings from `openings`, room labels at polygon centroids, a draggable viewer dot (pointermove while down = teleport + keep heading).
- Mobile: plan collapsed to a corner thumbnail, tap to expand; first-person via drag-look + two virtual sticks (or tap-to-walk by raycasting floor).

## Loading
- `GLTFLoader` + `MeshoptDecoder` (`three/addons/libs/meshopt_decoder.module.js`); add `KTX2Loader` (`setTranscoderPath` to a copied `basis/` folder, `detectSupport(renderer)`) if textures are KTX2; `DRACOLoader` only if Draco was used. Pin three.js via importmap to an exact version; ship it from `node_modules`/vendor copy or jsDelivr with exact version.
- Use relative URLs (`./house.glb`) - GitHub Pages serves under `/home-design/`. Add `.nojekyll`. Pages serves gzip but not brotli for .glb; meshopt/KTX2 already compress.
- Progress UI: `loader.loadAsync(url, onProgress)`; show percent. Keep the GLB < ~40 MB for mobile (split per room + lazy-load if bigger).

## Lighting/materials in the viewer
- Baked: see blender-bake-lightmaps; set `texture.channel = 1`, `flipY = false`, `mat.lightMap`. Disable `renderer.toneMapping` when the bake is display-referred. No real-time lights, or a faint `AmbientLight`/`HemisphereLight` to lift lightmap-less objects.
- Glass: names containing `glass` -> `transparent, opacity ~0.15, depthWrite=false`.
- Anisotropy: `texture.anisotropy = renderer.capabilities.getMaxAnisotropy()` on floor textures.
- `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`; `outputColorSpace` default sRGB is correct.

## Controls
- First-person: `PointerLockControls` + WASD at 1.4-1.6 m/s, eye height 1.6, `camera.fov` 70, near 0.05. Collision: short raycasts (0.35 m) horizontally at 1.0 m height against the shell (`viewer.example.js: blocked`), good enough for a house; upgrade to `three-mesh-bvh` if slow. Stairs: raycast down for floor height (smooth with lerp) instead of fixed `EYE`.
- Orbit: `OrbitControls` toggled with `O`; restrict `maxPolarAngle`, target to room centre. Touch devices use drag-look (PointerLock unsupported on iOS).
- Keep `camera.rotation.order='YXZ'` (PointerLockControls does) so roll stays zero.

## Test
- `node plan.test.mjs` verifies round-trip mapping, entrance at bottom, heading orientation, point-in-polygon. Extend the test whenever coordinates change.
- Browser check via Playwright: load page, evaluate `camera.position`, assert the plan dot pixel equals `toCanvas(...)`; screenshot at spawn.

## Sources
- three.js docs (GLTFLoader, PointerLockControls, MeshStandardMaterial lightMap, Texture.channel) https://threejs.org/docs/
- Lightmap via UV1 in glTF discussion https://discourse.threejs.org/t/why-should-i-use-lightmap-instead-of-draw-shadow-in-diffusemap/46759
- three.js skill pack for reference (materials etc.) https://github.com/CloudAI-X/threejs-skills
- Compression/decoder setup https://app.cinevva.com/guides/optimize-glb-for-web ; https://gltf-transform.dev/cli
- Coordinate mapping verified against Blender 5.1.1 glTF export; plan.mjs verified with node.
