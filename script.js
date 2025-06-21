// script.js

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('modelCanvas'), alpha: true });
renderer.setSize(300, 300); 

camera.position.z = 2;

const light = new THREE.HemisphereLight(0xffffff, 0x444444);
scene.add(light);

const loader = new window.THREE.GLTFLoader();

loader.load(
  'photorealistic_plant.glb',
  function (gltf) {
    scene.add(gltf.scene);
  },
  undefined,
  function (error) {
    console.error('Error loading GLB model:', error);
  }
);

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

animate();
