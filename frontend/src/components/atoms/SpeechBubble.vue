<template>
  <div speech-bubble pbottom aleft>
    <slot></slot>
  </div>
</template>
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

/* bottom and top  */
[speech-bubble][pbottom]::before {
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
</style>
