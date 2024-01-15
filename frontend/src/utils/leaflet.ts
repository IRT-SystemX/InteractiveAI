// @ts-nocheck

let newDestination
let originalDestTooltip
let actionId
let savedAction
const previousState = null
let drawFirstTripPolyline = true
let destMarkerisVisible = false
let endTripPolylineisVisible = false
function displayStats(value, event) {
  hideAllSynops()
  document
    .querySelectorAll('#synoptique button.btn-group-synoptic-active')
    .forEach((bouton) => bouton.classList.remove('btn-group-synoptic-active'))
  event.srcElement.classList.add('btn-group-synoptic-active')
  switch (value) {
    case 'STAT':
      document.getElementById('STATUS_nominal').hidden = false
      break
    case 'ECS':
      document.getElementById('ECS_nominal').hidden = false
      break
    case 'ELEC':
      document.getElementById('ELEC_nominal').hidden = false
      break
    case 'FUEL':
      document.getElementById('FUEL_nominal').hidden = false
      break
    case 'HYD':
      document.getElementById('HYD_nominal').hidden = false
      break
    case 'BLD':
      document.getElementById('BLEED_nominal').hidden = false
      break
    case 'TEST':
      document.getElementById('TEST_nominal').hidden = false
      break
    case 'ENG':
      document.getElementById('ENGINE_nominal').hidden = false
      break
  }
}

function hideAllSynops() {
  const synops = ['STATUS', 'ECS', 'ELEC', 'FUEL', 'HYD', 'BLEED', 'TEST', 'ENGINE']
  for (let synop = 0; synop < synops.length; synop++) {
    try {
      document.getElementById(synops[synop]).hidden = true
    } catch (error) {
      console.log('unknown synop element')
    }
    try {
      document.getElementById(synops[synop] + '_nominal').hidden = true
    } catch (error) {
      console.log('unknown synop nominal element')
    }
  }
}

function setDANotifications() {
  try {
    setCardsForDA()
    setDescsForDA()
  } catch (error) {}
}
function setCardsForDA() {
  const cards = document.getElementsByClassName('card')
  for (let card = 0; card < cards.length; card++) {
    if (
      !cards[card].classList.contains('DA_Card') ||
      !cards[card].classList.contains('light-card-detail-unselected-DA-MED')
    ) {
      cards[card].classList += ' DA_Card light-card-detail-unselected-DA-MED'
    }
  }
}

function setDescsForDA() {
  const descs = document.getElementsByClassName('p-1')
  for (let desc = 0; descs.length; desc++) {
    descs[desc].textContent = ''
  }
}

function clearMarkers() {
  markersDA.forEach(function (marker) {
    map.removeLayer(marker)
  })
  markersDA = []
}

function selectFlightPlan(actionId) {
  map.eachLayer(function (layer) {
    if (
      (layer instanceof L.Polyline && layer.options.polyLineId == 'endTripPolyline') ||
      (layer instanceof L.Polyline && layer.options.polyLineId == 'firstTripPolyline') ||
      (layer instanceof L.Polyline && layer.options.actionId != 'action_' + actionId)
    ) {
      map.removeLayer(layer)
      drawFirstTripPolyline = false
    } else {
      if (layer instanceof L.Polyline) {
        layer.setStyle({ color: 'gray', weight: 5 })
      }
    }
  })
  map.eachLayer(function (layer) {
    if (
      layer instanceof L.Marker &&
      layer.options.actionId != 'action_' + actionId &&
      !layer.options.isPlane
    ) {
      map.removeLayer(layer)
    }
  })
  // document.querySelectorAll(".new-dest-original-dest-tooltip").forEach(function(element){element.remove()});
}

function getMarkersCoordinates() {
  const CTX_URL_MOCK = 'http://localhost:4200/shared/json_samples/da_ctx.json'
  const CTX_URL = host + '/cabcontext/api/v1/contexts'
  const request = new XMLHttpRequest()
  request.onreadystatechange = function () {
    if (request.readyState == 4) {
      try {
        const response = JSON.parse(request.responseText)[0]
        latitude = response.data.Latitude
        longitude = response.data.Longitude
        altitude = response.data.Altitude
        destination = response.data.ApDest
        dest_lat = destination.aplat
        dest_lon = destination.aplon

        apname = destination.apname
        beautifyApName = apname.charAt(0).toUpperCase() + apname.slice(1).toLowerCase()

        if (!destMarkerisVisible) {
          // TODO: temporary fix for 05/12 demo -> need to add an id and then remove it when new dest chosen
          destMarker = new L.Marker([dest_lat, dest_lon])
          destMarker.addTo(map)
          destMarker.bindTooltip(beautifyApName, {
            permanent: true,
            direction: 'bottom',
            className: 'original-dest-tooltip'
          })
          destMarkerisVisible = true
        }

        response.data.wpList.forEach(function (marker, index, array) {
          const customIcon = L.icon({
            iconUrl: './assets/images/Ellipse.svg',
            iconSize: [20, 20]
          })
          markersDA.forEach(function (existingMarker) {
            const isMarkerStillPresent = response.data.wpList.some(function (newMarker) {
              return existingMarker.options.id === newMarker.wpidx
            })

            if (!isMarkerStillPresent) {
              map.removeLayer(existingMarker)
              markersDA = markersDA.filter(function (marker) {
                return marker.options.id !== existingMarker.options.id
              })
            }

            const polylineToRemove = getPolylineByWpId(existingMarker.options.id)
            if (polylineToRemove) {
              map.removeLayer(polylineToRemove)
            }
          })

          let wp = markersDA.find((existingMarker) => existingMarker.options.id === marker.wpidx)

          if (!wp) {
            wp = new L.Marker([marker.wplat, marker.wplon], {
              id: marker.wpidx,
              icon: customIcon
            })
            wp.addTo(map).bindPopup(marker.wpid)

            markersDA.push(wp)
          } else {
            wp.setLatLng([marker.wplat, marker.wplon])
          }

          const existingTooltip = wp.getTooltip()
          if (existingTooltip) {
            existingTooltip.setContent(marker.wpid)
          } else {
            wp.bindTooltip(marker.wpid, {
              permanent: true,
              direction: 'top',
              className: 'marker-tooltip'
            })
          }

          if (index < array.length - 1) {
            setTimeout(function () {
              connectMarkers(marker.wpidx, array[index + 1].wpidx)
            }, 100 * index)
          }
        })

        const lastWp = markersDA[markersDA.length - 1].getLatLng()
        const destLatLng = destMarker.getLatLng()
        const latlngs = [lastWp, destLatLng]
        if (!endTripPolylineisVisible) {
          const polyline = L.polyline(latlngs, {
            color: routeColorDA,
            weight: 10,
            polyLineId: 'endTripPolyline'
          }).addTo(map)
          endTripPolylineisVisible = true
        }
        const originalDestToolTip = document.querySelector('.original-dest-tooltip')
        if (originalDestToolTip) {
          applyTooltipStyles(originalDestToolTip)
        }
      } catch (error) {
        latitude = 3.3671419444444446
        longitude = 48.28990115416667
      }
    }
  }

  request.open('GET', CTX_URL, true)
  request.setRequestHeader('Accept', 'application/json')
  request.setRequestHeader('Authorization', 'Bearer ' + token)
  request.send()
}

function getPolylineByWpId(wpId) {
  let matchingPolyline = null

  map.eachLayer(function (layer) {
    if (layer instanceof L.Polyline && layer.options.polyLineId === 'firstTripPolyline') {
      const latlngs = layer.getLatLngs()
      const wpIds = latlngs.map((wp) => wp.options.id)

      if (wpIds.includes(wpId)) {
        matchingPolyline = layer
      }
    }
  })

  return matchingPolyline
}

function connectMarkers(markerId1, markerId2) {
  try {
    const marker1 = markersDA.find((marker) => marker.options.id === markerId1)
    const marker2 = markersDA.find((marker) => marker.options.id === markerId2)

    if (!marker1 || !marker2) {
      throw new Error('Les marqueurs avec les IDs fournis ne sont pas trouvés.')
    }

    const coordinatesChanged = markersDA.some(function (marker) {
      return (
        marker.getLatLng().equals(marker1.getLatLng()) ||
        marker.getLatLng().equals(marker2.getLatLng())
      )
    })

    if (coordinatesChanged) {
      //  clearPolylines();
    } else {
      return
    }

    const latlngs = [
      [marker1.getLatLng().lat, marker1.getLatLng().lng],
      [marker2.getLatLng().lat, marker2.getLatLng().lng]
    ]
    if (drawFirstTripPolyline) {
      const polyline = L.polyline(latlngs, {
        color: routeColorDA,
        weight: 10,
        polyLineId: 'firstTripPolyline'
      }).addTo(map)
    }
  } catch (error) {
    console.error(error.message)
  }
}

function askRecoDA() {
  document.getElementById('btnCarte').click()
  document.getElementById('dassault_assist').hidden = false
  document.getElementById('nominal_assist_en').hidden = true
  getRecommandationDA()
}

function setPolylineColor(color) {
  map.eachLayer(function (layer) {
    if (layer instanceof L.Polyline) {
      routeColorDA = color
      layer.setStyle({ color: routeColorDA })
    }
  })
  planeMarker.setIcon(plainFailedIcon)
  const oldDestTooltip = document.querySelector('.original-dest-tooltip')
  oldDestTooltip.style.backgroundColor = '#FF0000'
  oldDestTooltip.style.color = 'white'
  oldDestTooltip.style.fontWeight = 'bold'
  oldDestTooltip.style.fontSize = '18px'
  oldDestTooltip.style.borderRadius = '5px'
}
function setAndUpdateDAMarkersOnMap(data) {
  planeMarker.setLatLng([data.Latitude, data.Longitude])
}
function getRecommandationDA() {
  document.getElementById('da_recommendations').innerHTML = ''
  const xhr = new XMLHttpRequest()
  xhr.withCredentials = true
  xhr.addEventListener('readystatechange', function () {
    if (this.readyState === 4) {
      Swal.hideLoading()
      Swal.close()
      document.body.style.cursor = 'unset'
      console.log(JSON.parse(this.responseText))
      const recos = JSON.parse(this.responseText)
      let bodyHTML = ''
      for (let reco = 0; reco < recos.length; reco++) {
        const description = recos[reco].description
        const agent_type = recos[reco].agent_type
        const title = recos[reco].title
        const actions = recos[reco].actions
        sessionStorage.setItem('actions' + '[' + reco + ']', JSON.stringify(actions[0]))
        drawNewTrip(actions[0], reco)
        bodyHTML =
          "<div onclick ='" +
          'showDescDA(' +
          reco +
          '),getActionOnMap(' +
          reco +
          ')' +
          " '><span class='rtePrd reco'><b>" +
          title +
          '</b></span>'
        bodyHTML +=
          "<span style='bottom: 0px;position: absolute;' id='description" +
          reco +
          "' hidden>" +
          '<u>Flight Plan Information</u><br>' +
          description +
          '</span>'
        document.getElementById('da_recommendations').innerHTML += bodyHTML
      }
      btnValid =
        "<button style='margin-top:50px;float:right' class='da_assist_btn' onclick='gotoDestDA()'> Go to selected Destination</button>"
      document.getElementById('da_recommendations').innerHTML += btnValid
      const buttons = document.querySelectorAll('.rtePrd.reco')

      buttons.forEach(function (button) {
        button.addEventListener('click', handleClick)
      })
    }
  })
  xhr.open('POST', this.host + '/cab_recommendation/api/v1/recommendation')
  // xhr.open("GET", "http://localhost:4200/shared/json_samples/recommandations.json");
  xhr.setRequestHeader('Content-Type', 'application/json')
  xhr.setRequestHeader('Authorization', 'Bearer ' + window.localStorage.token)
  //todo : remplacer par l'event
  const recommendationBody = {
    event: {
      event_type: '90 PRESS : CABIN ALT TOO HIGH'
    }
  }
  xhr.send(JSON.stringify(recommendationBody))
}

function drawNewTrip(actions, reco) {
  const apname = actions.airport_destination.apname
  const newLatitude = actions.airport_destination.latitude
  const newLongitude = actions.airport_destination.longitude
  const newWaypoints = actions.waypoints
  actionId = 'action_' + reco

  console.log('Nouveau voyage ' + apname + ' tracé!')
  const polylineColors = ['#00A3FF', 'gray', 'white']

  const waypointIcon = L.icon({
    iconUrl: './assets/images/Ellipse.svg',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -10]
  })

  for (let i = 0; i < newWaypoints.length - 1; i++) {
    const waypoint1 = newWaypoints[i]
    const waypoint2 = newWaypoints[i + 1]

    const marker = L.marker([waypoint1.latitude, waypoint1.longitude], {
      icon: waypointIcon,
      actionId: actionId
    }).addTo(map)

    const latlngs = [
      [waypoint1.latitude, waypoint1.longitude],
      [waypoint2.latitude, waypoint2.longitude]
    ]
    const polyline = L.polyline(latlngs, {
      color: polylineColors[reco],
      weight: 5,
      actionId: actionId
    }).addTo(map)

    marker.bindTooltip(waypoint1.wpid, {
      permanent: true,
      direction: 'bottom',
      className: 'waypoint-tooltip',
      actionId: actionId
    })

    const waypointTooltips = document.querySelectorAll('.waypoint-tooltip')
    waypointTooltips.forEach(function (tooltip) {
      tooltip.style.backgroundColor = 'gray'
      tooltip.style.color = 'white'
    })
  }

  const lastWaypoint = newWaypoints[newWaypoints.length - 1]
  const lastWaypointMarker = L.marker([lastWaypoint.latitude, lastWaypoint.longitude], {
    icon: waypointIcon,
    actionId: actionId
  }).addTo(map)

  lastWaypointMarker.bindTooltip(lastWaypoint.wpid, {
    permanent: true,
    direction: 'bottom',
    className: 'waypoint-tooltip',
    actionId: actionId
  })

  const latlngs = [
    [lastWaypoint.latitude, lastWaypoint.longitude],
    [newLatitude, newLongitude]
  ]
  const polyline = L.polyline(latlngs, {
    color: polylineColors[reco],
    weight: 5,
    actionId: actionId
  }).addTo(map)

  const destinationIcon = L.icon({
    iconUrl: './assets/images/icon _flag_.png',
    iconSize: [50, 50]
  })

  const destMarker = L.marker([newLatitude, newLongitude], {
    icon: destinationIcon,
    actionId: actionId
  }).addTo(map)
  beautifyApName = apname.charAt(0).toUpperCase() + apname.slice(1).toLowerCase()
  destMarker.bindTooltip(beautifyApName, {
    permanent: true,
    direction: 'bottom',
    className: 'new-dest-original-dest-tooltip',
    actionId: actionId
  })

  const destTooltips = document.querySelectorAll('.new-dest-original-dest-tooltip')
  destTooltips.forEach(function (tooltip) {
    applyTooltipStyles(tooltip)
  })
}
function applyTooltipStyles(tooltip) {
  tooltip.style.backgroundColor = '#00A3FF'
  tooltip.style.color = 'black'
  tooltip.style.border = '1px solid black'
  tooltip.style.fontWeight = 'bold'
  tooltip.style.fontSize = '18px'
  tooltip.style.borderRadius = '5px'
}

function getActionOnMap(actionId) {
  savedAction = actionId
  actionId = 'action_' + actionId
  map.eachLayer(function (layer) {
    if (
      layer instanceof L.Polyline &&
      layer.options.polyLineId != 'firstTripPolyline' &&
      layer.options.polyLineId != 'endTripPolyline'
    ) {
      if (layer.options.actionId === actionId) {
        console.log("Polyligne associée à l'action:", layer)
        layer.setStyle({ color: '#00A3FF', weight: 15 })
      } else {
        layer.setStyle({ color: 'gray', weight: 5 })
      }
    }
  })

  map.eachLayer(function (layer) {
    if (layer instanceof L.Marker) {
      if (layer.options.actionId === actionId) {
        console.log("Marqueur associé à l'action:", layer)
      }
    }
  })
}
function gotoDestDA(dest, reco) {
  Swal.fire({
    icon: 'question',
    title:
      'You are about to recalculate a new flight plan to reroute to ' +
      newDestination +
      '<br>Do you wish to continue ? ',
    showCancelButton: true,
    showConfirmButton: true,
    cancelButtonText: 'No',
    confirmButtonText: 'Yes'
  })
    .then((result) => {
      if (result.isConfirmed) {
        traceInHistory('AWARD', authorizedUseCase, {})
        selectFlightPlan(savedAction)
      }
    })
    .finally(() => {
      // Go back to procedure view
      document.getElementsByTagName('procedure-component')[0].hidden = false
    })
}

function handleClick(event) {
  document.getElementById('da_recommendations').addEventListener('click', function (event) {
    const clickedElement = event.target
    const targetElement = clickedElement.closest('.rtePrd.reco')
    if (targetElement) {
      document.querySelectorAll('.rtePrd.reco').forEach((button) => {
        button.classList.remove('active_reco')
        button.parentElement.classList.remove('active_reco')
      })
      targetElement.classList.add('active_reco')
      newDestination = targetElement.innerText
    }
  })
}
