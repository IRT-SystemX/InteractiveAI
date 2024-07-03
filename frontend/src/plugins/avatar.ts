import gsap from 'gsap'
import {
  AmbientLight,
  Clock,
  Color,
  DirectionalLight,
  LoadingManager,
  Mesh,
  Object3D,
  PerspectiveCamera,
  Plane,
  Raycaster,
  Scene,
  Vector2,
  Vector3,
  WebGLRenderer
} from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { ref } from 'vue'

import { getCSSVariable } from '@/utils/utils'

const EASE_AMOUNT = 8

const scene = new Scene()
export const loading = ref(true)
export const manager = new LoadingManager(() => (loading.value = false))

const camera = new PerspectiveCamera(60, 1, 1, 1000)
camera.position.set(0, 0, 5)

const light = new DirectionalLight(0xffffff, 0.5)
light.position.setScalar(10)
scene.add(light)
scene.add(new AmbientLight(0xffffff, 1))

export const robot = new Object3D()
scene.add(robot)

const loader = new GLTFLoader(manager).setPath('/model/')
loader.load('robot.glb', function (gltf) {
  gltf.scene.scale.setScalar(4.4)
  robot.add(gltf.scene)
})

const plane = new Plane(new Vector3(0, 0, 1), -2)
const raycaster = new Raycaster()
const mouse = new Vector2()

const clock = new Clock()
const pointOfIntersection = new Vector3()

const look = new Vector2(0, 0)
function update() {
  look.x += (mouse.x * 2 - look.x) / EASE_AMOUNT
  look.y += (mouse.y * 2 - look.y) / EASE_AMOUNT
  raycaster.setFromCamera(look, camera)
  raycaster.ray.intersectPlane(plane, pointOfIntersection)
  robot.lookAt(pointOfIntersection)
}

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

export function setup(canvas: HTMLCanvasElement) {
  const renderer = new WebGLRenderer({
    antialias: true,
    alpha: true,
    canvas: canvas
  })
  renderer.setClearColor(0x000000, 0)

  document.addEventListener(
    'mousemove',
    (event: MouseEvent) => {
      mouse.x =
        (event.clientX - canvas.getBoundingClientRect().left - canvas.width / 2) / window.innerWidth
      mouse.y = -(
        (event.clientY - canvas.getBoundingClientRect().top - canvas.height / 2) /
        window.innerHeight
      )
    },
    true
  )

  let visible = !!canvas.offsetParent

  renderer.setAnimationLoop(() => {
    const time = clock.getElapsedTime()
    robot.position.y = Math.cos(time) * 0.3
    if (visible !== !!canvas.offsetParent) {
      visible = !!canvas.offsetParent
      renderer.setSize(canvas.width, canvas.height, false)
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

  return renderer
}

export function changeTexture(status: string) {
  robot.traverse((node) => {
    if (node instanceof Mesh) {
      //if (node.name === 'Head')
      //  node.material.map = new TextureLoader().load(`/model/${status}.png`)
      if (node.name === 'Button') {
        switch (status) {
          case 'default':
            node.material.emissive = new Color('#00a3ff')
            break
          case 'error':
          case 'success':
          case 'warning':
            gsap.to(node.material.emissive, {
              duration: 1,
              ease: 'elastic.out(1, 0.1)',
              ...new Color(getCSSVariable(`color-${status}`))
            })
        }
      }
    }
  })
}
