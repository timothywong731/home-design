// Minimal walkthrough: GLB + lightmaps + first-person/orbit + live 2D plan. Untested in a browser; plan.mjs maths is node-tested.
// index.html: importmap { "three": ".../three@<pin>/build/three.module.js", "three/addons/": ".../three@<pin>/examples/jsm/" },
//   <canvas id="plan" width="260" height="360"> overlaid bottom-left, <div id="room">.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { makeMap, drawPlan, planToThree, pointInPoly, threeToPlan } from './plan.mjs';

const EYE = 1.6, R = renderer();
function renderer() { const r = new THREE.WebGLRenderer({ antialias: true }); r.setPixelRatio(Math.min(devicePixelRatio, 2));
  r.setSize(innerWidth, innerHeight); r.toneMapping = THREE.NoToneMapping;  // lightmaps are already display-referred: do NOT tone-map twice
  document.body.appendChild(r.domElement); return r; }
const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 0.05, 60);
const house = await (await fetch('house.json')).json();                  // same file Blender used => plan and 3D cannot drift
const b = house.bounds;                                                   // {minX,minY,maxX,maxY} Blender metres
const ctx = document.getElementById('plan').getContext('2d'), map = makeMap(b, ctx.canvas.width, ctx.canvas.height);

const gltf = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync('house.glb');
scene.add(gltf.scene);
const lmLoader = new THREE.TextureLoader();
gltf.scene.traverse(o => {
  if (!o.isMesh) return;
  const m = o.material;
  // glTF cannot carry lightMap: ship lightmaps/<meshName>.webp beside the GLB (Blender 'Lightmap' UV layer is exported as TEXCOORD_1 -> geometry uv1)
  if (o.geometry.attributes.uv1) lmLoader.load(`lightmaps/${o.name}.webp`, t => {
    t.channel = 1; t.flipY = false; t.colorSpace = THREE.SRGBColorSpace; m.lightMap = t; m.lightMapIntensity = 1; m.needsUpdate = true; }, undefined, () => {});
  if (o.name.includes('glass')) { m.transparent = true; m.opacity = 0.15; m.depthWrite = false; }
});
scene.add(new THREE.AmbientLight(0xffffff, 0.0));                         // lightMap supplies the light; raise only if too dark

const [sx, sy] = house.spawn || [0, 0.5];
const p = planToThree(sx, sy, EYE); cam.position.set(p.x, p.y, p.z); cam.lookAt(p.x, EYE, p.z - 1);   // -Z = into the house

const fp = new PointerLockControls(cam, R.domElement), orbit = new OrbitControls(cam, R.domElement);
orbit.enabled = false; let mode = 'walk';
R.domElement.addEventListener('click', () => mode === 'walk' && fp.lock());
addEventListener('keydown', e => { keys.add(e.code); if (e.code === 'KeyO') { mode = mode === 'walk' ? 'orbit' : 'walk'; orbit.enabled = mode === 'orbit'; if (mode === 'orbit') fp.unlock(); } });
addEventListener('keyup', e => keys.delete(e.code)); const keys = new Set();

// click on plan = teleport
ctx.canvas.addEventListener('pointerdown', e => { const r = ctx.canvas.getBoundingClientRect();
  const [bx, by] = map.toWorld((e.clientX - r.left) * ctx.canvas.width / r.width, (e.clientY - r.top) * ctx.canvas.height / r.height);
  const q = planToThree(bx, by, EYE); cam.position.set(q.x, q.y, q.z); });

const ray = new THREE.Raycaster(); const clock = new THREE.Clock();
function blocked(dir) { ray.set(new THREE.Vector3(cam.position.x, 1.0, cam.position.z), dir); ray.far = 0.35;
  return ray.intersectObject(gltf.scene, true).length > 0; }       // ponytail: ray-per-frame collision; use a navmesh/BVH if slow
function walk(dt) {
  const f = (keys.has('KeyW') || keys.has('ArrowUp')) - (keys.has('KeyS') || keys.has('ArrowDown'));
  const s = (keys.has('KeyD')) - (keys.has('KeyA')); if (!f && !s) return;
  const fwd = cam.getWorldDirection(new THREE.Vector3()).setY(0).normalize(), right = new THREE.Vector3(-fwd.z, 0, fwd.x);
  const v = fwd.multiplyScalar(f).add(right.multiplyScalar(s)).normalize();
  if (!blocked(v)) cam.position.addScaledVector(v, 1.6 * dt); cam.position.y = EYE;
}
function loop() { const dt = Math.min(clock.getDelta(), 0.05); if (mode === 'walk') walk(dt); else orbit.update();
  const [bx, by] = threeToPlan(cam.position); const room = house.rooms.find(r => pointInPoly(bx, by, r.polygon));
  document.getElementById('room').textContent = room ? room.name : '';
  drawPlan(ctx, map, house, cam, cam.fov, cam.aspect, room?.id); R.render(scene, cam); requestAnimationFrame(loop); }
addEventListener('resize', () => { cam.aspect = innerWidth / innerHeight; cam.updateProjectionMatrix(); R.setSize(innerWidth, innerHeight); });
loop();
