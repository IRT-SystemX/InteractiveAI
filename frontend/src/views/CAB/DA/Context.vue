<template>
  <Context
    v-model="activeTab"
    :tabs="[$t('cab.tab.map'), $t('cab.tab.synoptic'), $t('cab.tab.dependencies')]">
    <Map v-if="activeTab === 0"></Map>
    <div v-if="activeTab === 1">
      <div id="synoptique" class="imgMarged btn-group-synoptic">
        <button id="stat" class="button" style="border-top-left-radius: 5px; border-bottom-left-radius: 5px;" @click="($event) => displayStats('STAT', $event)">
          STAT
        </button><br>
        <button id="eng" class="button" @click="($event) => displayStats('ENG', $event)">
          ENG
        </button><br>
        <button id="elec" class="button" @click="($event) => displayStats('ELEC', $event)">
          ELEC
        </button>
        <button id="fuel" class="button" @click="($event) => displayStats('FUEL', $event)">
          FUEL
        </button><br>
        <button id="hyd" class="button" @click="($event) => displayStats('HYD', $event)">
          HYD
        </button><br>
        <button id="ecs" class="button" @click="($event) => displayStats('ECS', $event)">
          ECS
        </button>
        <button id="bld" class="button" @click="($event) => displayStats('BLD', $event)">
          BLD
        </button><br>
        <button id="test" class="button" style="border-top-right-radius: 5px; border-bottom-right-radius: 5px;" @click="($event) => displayStats('TEST', $event)">
          TEST
        </button><br>
      </div>
      <div id="synoptic_back">
        <img id = "ECS" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/ECS_cabin-alt-too-high.png' hidden>
        <img id = "ENGINE" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/ENGINE-eng1-out.png' hidden>
        <img id = "FUEL" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/FUEL-eng1-out.png' hidden>
        <img id = "ELEC" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/ELEC-gen1+2+3-fault.png' hidden>
        <img id = "HYD" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/HYD-eng1-out.png' hidden>
        <img id = "STATUS_nominal" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/STATUS_nominal.png' hidden>
        <img id = "ECS_nominal" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/ECS_nominal.png' hidden>
        <img id = "ELEC_nominal" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/ELEC_nominal.png' hidden>
        <img id = "FUEL_nominal" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/FUEL_nominal.png' hidden>
        <img id = "HYD_nominal" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/HYD_nominal.png' hidden>
        <img id = "BLEED_nominal" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/BLEED_nominal.png' hidden>
        <img id = "TEST_nominal" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/TEST_nominal.png' hidden>
        <img id = "ENGINE_nominal" class ='imgMarged daSyn' src='@/assets/img/placeholders/DA/ENGINE_nominal.png' hidden>
      </div>
    </div>
    <div v-if="activeTab === 2">2</div>
  </Context>
</template>
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

import Map from '@/components/organisms/Map.vue'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'

import Context from '../Common/Context.vue'

const activeTab = ref(0)

const servicesStore = useServicesStore()
const mapStore = useMapStore()

const contextId = ref(0)

onMounted(async () => {
  contextId.value = await servicesStore.getContext('DA', (context: any) => {
    mapStore.addContextWaypoint({ lat: context.Latitude, lng: context.Longitude, id: 'Plane' })
  })
})

onBeforeUnmount(() => {
  clearInterval(contextId.value)
})

const displayStats = (value: string, event: Event): void => {
  hideAllSynops();
  document.querySelectorAll("#synoptique button.btn-group-synoptic-active").forEach(bouton => bouton.classList.remove("btn-group-synoptic-active"));
  (event.target as HTMLElement).classList.add("btn-group-synoptic-active");
  switch (value) {
    case 'STAT':
      document.getElementById("STATUS_nominal")?.removeAttribute("hidden");
      break;
    case 'ECS':
      document.getElementById("ECS_nominal")?.removeAttribute("hidden");
      break;
    case 'ELEC':
      document.getElementById("ELEC_nominal")?.removeAttribute("hidden");
      break;
    case 'FUEL':
      document.getElementById("FUEL_nominal")?.removeAttribute("hidden");
      break;
    case 'HYD':
      document.getElementById("HYD_nominal")?.removeAttribute("hidden");
      break;
    case 'BLD':
      document.getElementById("BLEED_nominal")?.removeAttribute("hidden");
      break;
    case 'TEST':
      document.getElementById("TEST_nominal")?.removeAttribute("hidden");
      break;
    case 'ENG':
      document.getElementById("ENGINE_nominal")?.removeAttribute("hidden");
      break;
  }
};

const hideAllSynops = (): void => {
  var synops: string[] = ['STATUS', 'ECS', 'ELEC', 'FUEL', 'HYD', 'BLEED', 'TEST', 'ENGINE'];
  for (var synop = 0; synop < synops.length; synop++) {
    try {
      document.getElementById(synops[synop])?.setAttribute("hidden", "true");
    } catch (error) {
      console.log("unknown synop element");
    }
    try {
      document.getElementById(synops[synop] + "_nominal")?.setAttribute("hidden", "true");
    } catch (error) {
      console.log("unknown synop nominal element");
    }
  }
};
</script>
<style lang="scss">.btn-group-synoptic button {
  background-color: white;
  color: black;
  padding: 2px 24px;
  cursor: pointer;
  float: left;
}

.btn-group button:not(:last-child) {
  border-right: none;
}

.btn-group:after {
  content: "";
  clear: both;
  display: table;
}

.btn-group button:hover {
  background-color: #0085CC;
  color:white;
}
.btn-group-synoptic button:active,
.btn-group-synoptic button:hover,
.btn-group-synoptic button:focus,
.btn-group-synoptic-active {
  background-color: #9B9B9B!important
}
.btn-group-synoptic button{
  background: none;
  background-color: #4B4B4B;
  color:white;
  border: none;
  font-weight: bold;
}
.btn-group-synoptic{
  display: inline-flex;
  background: none;
  color: white;
}
.btn-group button:active,
.btn-group button:focus,
.btn-group button:hover,
.btn-group-active {
  background-color: #9B9B9B!important;
  color: white;
  border-radius: 32px;
  font-weight: bold;
}

#synoptic_back{
  background-color: black;
  height: 340px;
  width: 91%;
  border-radius: 7px;
}</style>
@/stores/components/map