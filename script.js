import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import { GLTFLoader } from 'https://unpkg.com/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 600 / 400, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true });
renderer.setSize(600, 400);
document.getElementById("model-viewer").appendChild(renderer.domElement);

const light = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
scene.add(light);

const loader = new GLTFLoader();
loader.load('assets/photorealistic_plant.glb', function (gltf) {
  scene.add(gltf.scene);
  gltf.scene.rotation.y = 1;
  camera.position.z = 2;

  function animate() {
    requestAnimationFrame(animate);
    gltf.scene.rotation.y += 0.003;
    renderer.render(scene, camera);
  }

  animate();
}, undefined, function (error) {
  console.error('Error loading model:', error);
});
