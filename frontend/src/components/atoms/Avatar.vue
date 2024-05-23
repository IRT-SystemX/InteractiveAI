<template>
  <div class="cab-avatar flex flex-center" :style="{ height: size + 'px', width: size + 'px' }">
    <LoadingVue v-if="loading" color="var(--color-primary)"></LoadingVue>
    <canvas
      ref="canvasHTML"
      :class="{ visible: !loading }"
      :height="size"
      :width="size"
      alt="CAB robot avatar"
      title="Model by sketchfab.com/MoraAzul"></canvas>
  </div>
</template>
<script setup lang="ts">
import {
  AmbientLight,
  Clock,
  Color,
  DirectionalLight,
  LoadingManager,
  Mesh,
  Object3D,
  type Object3DEventMap,
  PerspectiveCamera,
  Plane,
  Raycaster,
  Scene,
  Vector2,
  Vector3,
  WebGLRenderer
} from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import LoadingVue from './Loading.vue'

const canvasHTML = ref<HTMLCanvasElement>()
const props = withDefaults(defineProps<{ size: number; status?: 'default' | 'error' }>(), {
  size: 100,
  status: 'default'
})

const EASE_AMOUNT = 8
const loading = ref(true)
const rendererInstance = ref<WebGLRenderer>()
const robot = ref<Object3D<Object3DEventMap>>()

function changeTexture(status: (typeof props)['status']) {
  robot.value?.traverse((node) => {
    if (node instanceof Mesh) {
      // if (node.name === 'Head')
      //   node.material.map = new THREE.TextureLoader().load(`/model/${status}.png`)
      if (node.name === 'Button') {
        switch (status) {
          case 'default':
            node.material.emissive = new Color('#00a3ff')
            break
          case 'error':
            node.material.emissive = new Color('#f00')
        }
      }
    }
  })
}

onMounted(() => {
  const scene = new Scene()
  const manager = new LoadingManager()
  manager.onLoad = () => {
    loading.value = false
  }
  const camera = new PerspectiveCamera(60, 1, 1, 1000)
  camera.position.set(0, 0, 5)
  const renderer = new WebGLRenderer({
    antialias: true,
    alpha: true,
    canvas: canvasHTML.value!
  })
  rendererInstance.value = renderer
  renderer.setClearColor(0x000000, 0)
  const canvas = renderer.domElement

  const light = new DirectionalLight(0xffffff, 0.5)
  light.position.setScalar(10)
  scene.add(light)
  scene.add(new AmbientLight(0xffffff, 1))

  let base = new Object3D()
  scene.add(base)

  const loader = new GLTFLoader(manager).setPath('/model/')
  loader.load('robot.glb', function (gltf) {
    gltf.scene.scale.setScalar(4.4)
    base.add(gltf.scene)
    robot.value = base
    changeTexture(props.status)
  })

  const plane = new Plane(new Vector3(0, 0, 1), -2)
  const raycaster = new Raycaster()
  const mouse = new Vector2()

  const clock = new Clock()
  const pointOfIntersection = new Vector3()
  document.addEventListener('mousemove', onMouseMove, false)

  function onMouseMove(event: MouseEvent) {
    mouse.x =
      ((event.clientX - canvas.getBoundingClientRect().left - props.size / 2) / window.innerWidth) *
      2
    mouse.y =
      -(
        (event.clientY - canvas.getBoundingClientRect().top - props.size / 2) /
        window.innerHeight
      ) * 2
  }
  const look = new Vector2(0, 0)
  function update() {
    look.x += (mouse.x - look.x) / EASE_AMOUNT
    look.y += (mouse.y - look.y) / EASE_AMOUNT
    raycaster.setFromCamera(look, camera)
    raycaster.ray.intersectPlane(plane, pointOfIntersection)

    raycaster.setFromCamera(look, camera)
    raycaster.ray.intersectPlane(plane, pointOfIntersection)
    base.lookAt(pointOfIntersection)
  }

  let visible = !!canvas.offsetParent

  renderer.setAnimationLoop(() => {
    const time = clock.getElapsedTime()
    // changeTexture(Math.floor(time) % 2 ? 'error' : 'default')
    base.position.y = Math.cos(time * 2) * 0.3
    if (visible !== !!canvas.offsetParent) {
      visible = !!canvas.offsetParent
      renderer.setSize(props.size, props.size, false)
      camera.aspect = canvas.clientWidth / canvas.clientHeight
      camera.updateProjectionMatrix()
    }
    update()
    if (resize(renderer)) {
      camera.aspect = canvas.clientWidth / canvas.clientHeight
      camera.updateProjectionMatrix()
    }
    renderer.render(scene, camera)
  })

  function resize(renderer: WebGLRenderer) {
    const canvas = renderer.domElement
    const width = canvas.clientWidth
    const height = canvas.clientHeight
    const needResize = canvas.width !== width || canvas.height !== height
    if (needResize) {
      renderer.setSize(width, height, false)
    }
    return needResize
  }
})

onBeforeUnmount(() => {
  rendererInstance.value!.dispose()
})
</script>
<style scoped>
.cab-avatar {
  position: relative;
  img {
    position: absolute;
  }
  canvas {
    cursor: grab;
    position: absolute;
    opacity: 0;
    transition: 2s;
    &.visible {
      opacity: 1;
    }
    &:active {
      cursor: grabbing;
    }
  }
}
</style>
