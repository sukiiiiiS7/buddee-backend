// Load and display a .glb plant model using Three.js
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 16 / 9, 0.1, 1000);
camera.position.set(0, 1.2, 3);

const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(440, 248);
renderer.setClearColor(0x000000, 0);

const container = document.getElementById("modelContainer");
container.appendChild(renderer.domElement);

// Light setup
const light = new THREE.HemisphereLight(0xffffff, 0x444444, 1.2);
scene.add(light);

// Load GLB model
const loader = new THREE.GLTFLoader();
loader.load(
  "./assets/photorealistic_plant.glb",
  function (gltf) {
    const model = gltf.scene;
    model.scale.set(1.4, 1.4, 1.4);
    model.rotation.y = Math.PI;
    scene.add(model);
  },
  undefined,
  function (error) {
    console.error("Failed to load model:", error);
  }
);

// Animate scene
function animate() {
  requestAnimationFrame(animate);
  scene.rotation.y += 0.003;
  renderer.render(scene, camera);
}
animate();
