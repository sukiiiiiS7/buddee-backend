const canvas = document.getElementById('modelCanvas');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas, alpha: true });
renderer.setSize(canvas.clientWidth, canvas.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setClearColor(0x000000, 0); // transparent

const light = new THREE.HemisphereLight(0xffffff, 0x444444, 1.5);
scene.add(light);

const loader = new THREE.GLTFLoader();
loader.load('photorealistic_plant.glb', function (gltf) {
  const model = gltf.scene;
  model.scale.set(1.5, 1.5, 1.5);
  model.rotation.y = Math.PI; // rotate to face front
  scene.add(model);

  const animate = function () {
    requestAnimationFrame(animate);
    model.rotation.y += 0.005;
    renderer.render(scene, camera);
  };
  animate();
}, undefined, function (error) {
  console.error('GLB load error:', error);
});

camera.position.z = 5;

window.addEventListener('resize', () => {
  camera.aspect = canvas.clientWidth / canvas.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
});
