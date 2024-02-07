import { useColorMode } from '@vueuse/core'
import { nextTick } from 'vue'

import { Entities, EntitiesArray } from '@/entities/entities'

export const mode = useColorMode({
  emitAuto: true,
  modes: EntitiesArray.reduce(
    (a, v) => ({ ...a, [v]: `${Entities[v].darkMode ? 'dark' : 'light'} ${v}` }),
    {}
  )
})

const isAppearanceTransition =
  typeof document !== 'undefined' &&
  // @ts-expect-error: Transition API
  document.startViewTransition &&
  !window.matchMedia('(prefers-reduced-motion: reduce)').matches

/**
 * Credit to [@hooray](https://github.com/hooray)
 * @see https://github.com/vuejs/vitepress/pull/2347
 */
export function toggleMode(selectedMode: typeof mode.value) {
  if (!isAppearanceTransition) {
    mode.value = selectedMode
    return
  }
  const x = 0
  const y = 0
  const endRadius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y))
  // @ts-expect-error: Transition API
  const transition = document.startViewTransition(async () => {
    mode.value = selectedMode
    await nextTick()
  })
  transition.ready.then(() => {
    document.documentElement.animate(
      {
        clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${endRadius}px at ${x}px ${y}px)`]
      },
      {
        duration: 300,
        easing: 'ease-in',
        pseudoElement: '::view-transition-new(root)'
      }
    )
  })
}
