<!--from https://codepen.io/MarkBoots/pen/RwLPXgJ-->
<template>
  <div speech-bubble v-bind="[`p${position}`, `a${arrow}`]" aleft :flip="flip">
    <slot></slot>
  </div>
</template>
<script setup lang="ts">
defineProps<{
  position: 'top' | 'bottom' | 'left' | 'right'
  arrow: 'top' | 'bottom' | 'left' | 'right' | 'center'
  flip?: boolean
}>()
</script>
<style lang="scss">
[speech-bubble],
[speech-bubble] * {
  box-sizing: border-box;
}

[speech-bubble] {
  --bbColor: var(--color-grey-200);
  --bbArrowSize: 1.5rem;
  --bbBorderRadius: var(--radius-medium);
  --bbPadding: var(--spacing-1);
  background: var(--bbColor);
  border-radius: var(--bbBorderRadius);
  padding: var(--bbPadding);
  position: relative;
}

[speech-bubble]::before {
  content: '';
  position: absolute;
  background: var(--bbColor);
}

[speech-bubble][pbottom] {
  margin-bottom: var(--bbArrowSize);
}
[speech-bubble][ptop] {
  margin-top: var(--bbArrowSize);
}
[speech-bubble][pleft] {
  margin-left: var(--bbArrowSize);
}
[speech-bubble][pright] {
  margin-right: var(--bbArrowSize);
}

/* bottom and top  */
[speech-bubble][pbottom]::before,
[speech-bubble][ptop]::before {
  --width: calc(var(--bbArrowSize) / 2 * 3);
  height: var(--bbArrowSize);
  width: var(--width);
}

/* bottom */
[speech-bubble][pbottom]::before {
  top: calc(100% - 2px);
}
[speech-bubble][pbottom][aleft]::before {
  left: 1rem;
  clip-path: polygon(25% 0, 100% 0, 0% 100%);
}
[speech-bubble][pbottom][acenter]::before {
  left: calc(50% - var(--width) / 2);
  clip-path: polygon(12.5% 0, 87.5% 0, 50% 100%);
}
[speech-bubble][pbottom][aright]::before {
  right: 1rem;
  clip-path: polygon(0 0, 75% 0, 100% 100%);
}

/* top */
[speech-bubble][ptop]::before {
  bottom: calc(100% - 2px);
}
[speech-bubble][ptop][aleft]::before {
  left: var(--bbPadding);
  clip-path: polygon(0 0, 100% 100%, 25% 100%);
}
[speech-bubble][ptop][acenter]::before {
  left: calc(50% - var(--width) / 2);
  clip-path: polygon(12.5% 100%, 50% 0, 87.5% 100%);
}
[speech-bubble][ptop][aright]::before {
  right: var(--bbPadding);
  clip-path: polygon(0 100%, 100% 0, 75% 100%);
}

/* left and right  */
[speech-bubble][pleft]::before,
[speech-bubble][pright]::before {
  --height: calc(var(--bbArrowSize) / 2 * 3);
  width: var(--bbArrowSize);
  height: var(--height);
}

/* right */
[speech-bubble][pright]::before {
  left: calc(100% - 2px);
}
[speech-bubble][pright][atop]::before {
  top: var(--bbPadding);
  clip-path: polygon(100% 0, 0 100%, 0 25%);
}
[speech-bubble][pright][acenter]::before {
  top: calc(50% - var(--height) / 2);
  clip-path: polygon(0 12.5%, 100% 50%, 0 87.5%);
}
[speech-bubble][pright][abottom]::before {
  bottom: var(--bbPadding);
  clip-path: polygon(0 0, 100% 100%, 0 75%);
}

/* left */
[speech-bubble][pleft]::before {
  right: calc(100% - 2px);
}
[speech-bubble][pleft][atop]::before {
  top: var(--bbPadding);
  clip-path: polygon(0 0, 100% 25%, 100% 100%);
}
[speech-bubble][pleft][acenter]::before {
  top: calc(50% - var(--height) / 2);
  clip-path: polygon(0 50%, 100% 12.5%, 100% 87.5%);
}
[speech-bubble][pleft][abottom]::before {
  bottom: var(--bbPadding);
  clip-path: polygon(0 100%, 100% 0, 100% 75%);
}

/* flip */
[speech-bubble][pbottom][flip]::before,
[speech-bubble][ptop][flip]::before {
  transform: scaleX(-1);
}
[speech-bubble][pleft][flip]::before,
[speech-bubble][pright][flip]::before {
  transform: scaleY(-1);
}

/* for demo */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  cursor: default;
}
body {
  max-width: 60rem;
  margin-inline: auto;
  font-family: sans-serif;
  display: grid;
  grid-template-areas:
    'br bc bl'
    'rb cc lb'
    'rc cc lc'
    'rt cc lt'
    'tr tc tl';
  padding: 2rem;
  gap: 2rem;
  background: #141518;
}

.middle {
  grid-area: cc;
  align-self: center;
  justify-self: center;
  text-align: center;
  color: white;
}

[speech-bubble][pbottom][aleft] {
  grid-area: bl;
}
[speech-bubble][pbottom][acenter] {
  grid-area: bc;
}
[speech-bubble][pbottom][aright] {
  grid-area: br;
}

[speech-bubble][pright][atop] {
  grid-area: rt;
}
[speech-bubble][pright][acenter] {
  grid-area: rc;
}
[speech-bubble][pright][abottom] {
  grid-area: rb;
}

[speech-bubble][pleft][atop] {
  grid-area: lt;
}
[speech-bubble][pleft][acenter] {
  grid-area: lc;
}
[speech-bubble][pleft][abottom] {
  grid-area: lb;
}

[speech-bubble][ptop][aleft] {
  grid-area: tl;
}
[speech-bubble][ptop][acenter] {
  grid-area: tc;
}
[speech-bubble][ptop][aright] {
  grid-area: tr;
}

[speech-bubble][pbottom],
[speech-bubble][ptop] {
  margin: 0;
}

[speech-bubble] {
  filter: drop-shadow(0px 0px 0.2rem black);
  transition: transform 0.25s ease;
}
[speech-bubble]:hover {
  transform: scale(1.05);
  filter: drop-shadow(0px 0px 0.2rem black) drop-shadow(0px 0px 1rem var(--bbColor));
}

[speech-bubble] .title {
  font-weight: 600;
  color: white;
  text-shadow: 1px 1px 2px black;
  margin-bottom: 0.5rem;
}
[speech-bubble] code {
  background: white;
  margin: 0.125rem;
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  font-size: 0.9rem;
}

.middle code {
  font-size: 1rem;
}
</style>
