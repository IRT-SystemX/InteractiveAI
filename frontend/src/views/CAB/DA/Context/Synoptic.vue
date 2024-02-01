<template>
  <div>
    <div id="synoptique" class="imgMarged btn-group">
      <button
        v-for="button of tabs"
        :key="button"
        :class="{ active: tab === button }"
        @click="emit('update:tab', tab)">
        {{ button }}
      </button>
    </div>
    <div id="synoptic_back">
      <img
        :alt="tab"
        :src="asset(`assets/img/placeholders/DA/${tab}_${!faulty ? 'nominal' : 'faulty'}.png`)" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { asset } from '@/utils/utils'

const tabs = ['STAT', 'ENG', 'ELEC', 'FUEL', 'HYD', 'ECS', 'BLD'] as const
export type Tab = (typeof tabs)[number]

defineProps<{ faulty: boolean; tab: Tab }>()

const emit = defineEmits<{
  'update:tab': [tab: Tab]
}>()
</script>
<style lang="scss">
.btn-group button {
  background-color: white;
  color: black;
  padding: 2px 24px;
  cursor: pointer;
  float: left;
}

.btn-group button:first-child {
  border-radius: 4px 0 0 4px;
}

.btn-group button:last-child {
  border-radius: 0 4px 4px 0;
}

.btn-group button:not(:last-child) {
  border-right: none;
}

.btn-group:after {
  content: '';
  clear: both;
  display: table;
}

.btn-group button:hover {
  background-color: #0085cc;
  color: white;
}
.btn-group button:active,
.btn-group button:hover,
.btn-group button:focus,
.btn-group-active {
  background-color: #9b9b9b !important;
}
.btn-group button {
  background: none;
  background-color: #4b4b4b;
  color: white;
  border: none;
  font-weight: bold;
}
.btn-group {
  display: inline-flex;
  background: none;
  color: white;
}
.btn-group button:active,
.btn-group button:focus,
.btn-group button:hover,
.btn-group button.active,
.btn-group-active {
  background-color: #9b9b9b !important;
  color: white;
  border-radius: 32px;
  font-weight: bold;
}

#synoptic_back {
  background-color: black;
  height: 340px;
  width: 91%;
  border-radius: 7px;
}
</style>
