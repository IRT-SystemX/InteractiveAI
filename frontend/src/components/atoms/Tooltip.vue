<template>
  <div class="cab-tooltip">
    <slot />
    <div class="cab-tooltip-container"><slot name="tooltip"></slot></div>
  </div>
</template>
<script setup lang="ts"></script>
<style lang="scss">
.cab-tooltip {
  display: inline-block;
  border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
  &:hover &-container {
    visibility: visible;
  }
  &-container {
    visibility: hidden;
    width: 120px;
    background-color: black;
    color: #fff;
    text-align: center;
    padding: 5px 0;
    border-radius: 6px;
    transform: translateX(-50%);

    /* Position the tooltip text - see examples below! */
    position: absolute;
    z-index: 1;
    &::after {
      content: ' ';
      position: absolute;
      bottom: 100%; /* At the top of the tooltip */
      left: 50%;
      margin-left: -5px;
      border-width: 5px;
      border-style: solid;
      border-color: transparent transparent black transparent;
    }
  }
}
</style>
