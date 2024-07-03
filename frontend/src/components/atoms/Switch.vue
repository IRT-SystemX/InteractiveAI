<template>
  <div class="cab-switch">
    <input v-model="value" type="checkbox" />
    <span class="slider round"></span>
  </div>
</template>
<script setup lang="ts">
const value = defineModel<boolean>()
withDefaults(defineProps<{ size?: number }>(), { size: 16 })
</script>
<style lang="scss">
.cab-switch {
  position: relative;
  display: inline-block;
  width: calc(v-bind('size') * 1.75 * 1px);
  height: calc(v-bind('size') * 1px);
  align-content: center;
  vertical-align: middle;
  input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--color-grey-300);
    transition: var(--duration);
  }

  .slider:before {
    position: absolute;
    content: '';
    height: calc(v-bind('size') / 8 * 6 * 1px);
    width: calc(v-bind('size') / 8 * 6 * 1px);
    left: calc(v-bind('size') * 1px / 8);
    bottom: calc(v-bind('size') * 1px / 8);
    background-color: var(--color-primary);
    transition: var(--duration);
  }

  input:checked + .slider {
    background-color: var(--color-primary);

    &:before {
      background-color: #fff;
    }
  }

  input:checked + .slider:before {
    transform: translateX(calc(v-bind('size') / 8 * 6 * 1px));
  }

  /* Rounded sliders */
  .slider.round {
    border-radius: var(--radius-circular);
  }

  .slider.round:before {
    border-radius: 50%;
  }
}
</style>
