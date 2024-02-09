import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Button from '../Button.vue'

describe('Button', () => {
  it('renders properly', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Test button'
      }
    })
    expect(wrapper.text()).toContain('Test button')
  })
})
