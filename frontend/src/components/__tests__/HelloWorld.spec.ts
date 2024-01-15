import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SVG from '../atoms/SVG.vue'

describe('HelloWorld', () => {
  it('renders properly', () => {
    const wrapper = mount(SVG)
    expect(wrapper.text()).toContain('Hello Vitest')
  })
})
