function displayStats(value, event) {
    hideAllSynops()
    document.querySelectorAll("#synoptique button.btn-group-synoptic-active").forEach(bouton => bouton.classList.remove("btn-group-synoptic-active"));
    event.srcElement.classList.add("btn-group-synoptic-active");
    switch (value) {
      case 'STAT':
        document.getElementById("STATUS_nominal").hidden = false;
        break;
      case 'ECS':
        document.getElementById("ECS_nominal").hidden = false;
        break;
      case 'ELEC':
        document.getElementById("ELEC_nominal").hidden = false;
        break;
      case 'FUEL':
        document.getElementById("FUEL_nominal").hidden = false;
        break;
      case 'HYD':
        document.getElementById("HYD_nominal").hidden = false;
        break;
      case 'BLD':
        document.getElementById("BLEED_nominal").hidden = false;
        break;
      case 'TEST':
        document.getElementById("TEST_nominal").hidden = false;
        break;
      case 'ENG':
        document.getElementById("ENGINE_nominal").hidden = false;
        break;
    }
  }

  function hideAllSynops() {
    var synops = ['STATUS', 'ECS', 'ELEC', 'FUEL', 'HYD', 'BLEED', 'TEST', 'ENGINE'];
    for (var synop = 0; synop < synops.length; synop++) {
      try {
        document.getElementById(synops[synop]).hidden = true;
      } catch (error) {
        console.log("unknown synop element")
      }
      try {
        document.getElementById(synops[synop] + "_nominal").hidden = true;
      } catch (error) {
        console.log("unknown synop nominal element")
      }
    }
  }

  function setDANotifications() {
    try {
      setCardsForDA();
      setDescsForDA();
    } catch (error) {
    }

  }
  function setCardsForDA() {
    var cards = document.getElementsByClassName("card");
    for (var card = 0; card < cards.length; card++) {
      if (!cards[card].classList.contains("DA_Card") || !cards[card].classList.contains("light-card-detail-unselected-DA-MED")) {
        cards[card].classList += " DA_Card light-card-detail-unselected-DA-MED";
      }
    }
  }

  function setDescsForDA() {
    var descs = document.getElementsByClassName("p-1");
    for (var desc = 0; descs.length; desc++) {
      descs[desc].textContent = "";
    }
  }

  function clearMarkers() {
    markersDA.forEach(function (marker) {
      map.removeLayer(marker);
    });
    markersDA = [];
  }

  function clearPolylines() {
    map.eachLayer(function (layer) {
      if (layer instanceof L.Polyline) {
        map.removeLayer(layer);
      }
    });
  }


  function getMarkersCoordinates() {
    var CTX_URL_MOCK = "http://localhost:4200/shared/json_samples/da_ctx.json";
    var CTX_URL = host + "/cabcontext/api/v1/contexts";
    var request = new XMLHttpRequest();
    // clearMarkers();
    request.onreadystatechange = function () {
      if (request.readyState == 4) {
        try {
          var response = JSON.parse(request.responseText)[0];
          latitude = response.data.Latitude;
          longitude = response.data.Longitude;
          altitude = response.data.Altitude;
          destination = response.data.ApDest;
          dest_lat = destination.aplat;
          dest_lon = destination.aplon;

          destMarker = new L.Marker([dest_lat, dest_lon]);
          destMarker.addTo(map);
          destMarker.bindTooltip(destination.apname, { permanent: true, direction: 'bottom', className: 'dest-tooltip' });

          response.data.wpList.forEach(function (marker, index, array) {
            var customIcon = L.icon({
              iconUrl: './assets/images/Ellipse.svg',
              iconSize: [20, 20]
            });

            var wp = new L.Marker([marker.wplat, marker.wplon], {
              id: marker.wpidx,
              icon: customIcon,
            });
            wp.bindTooltip(marker.wpid, { permanent: true, direction: 'top', className: 'marker-tooltip' });

            wp.addTo(map).bindPopup(marker.wpid);

            markersDA.push(wp);

            if (index < array.length - 1) {
              setTimeout(function () {
                connectMarkers(marker.wpidx, array[index + 1].wpidx);
              }, 100 * index);
            }
          });
          var lastWp = markersDA[markersDA.length - 1].getLatLng();
          var destLatLng = destMarker.getLatLng();
          var latlngs = [lastWp, destLatLng];
          var polyline = L.polyline(latlngs, { color: routeColorDA, weight: 10 }).addTo(map);

        } catch (error) {
          latitude = 3.3671419444444446;
          longitude = 48.28990115416667;
        }

      }
    };

    request.open("GET", CTX_URL, true);
    request.setRequestHeader("Accept", "application/json");
    request.setRequestHeader("Authorization", "Bearer " + token);
    request.send();
  }


  function connectMarkers(markerId1, markerId2) {
    try {
      var marker1 = markersDA.find(marker => marker.options.id === markerId1);
      var marker2 = markersDA.find(marker => marker.options.id === markerId2);

      if (!marker1 || !marker2) {
        throw new Error('Les marqueurs avec les IDs fournis ne sont pas trouvés.');
      }

      var coordinatesChanged = markersDA.some(function (marker) {
        return marker.getLatLng().equals(marker1.getLatLng()) || marker.getLatLng().equals(marker2.getLatLng());
      });

      if (coordinatesChanged) {
        //  clearPolylines();
      } else {
        return;
      }

      var latlngs = [
        [marker1.getLatLng().lat, marker1.getLatLng().lng],
        [marker2.getLatLng().lat, marker2.getLatLng().lng],
      ];
      var polyline = L.polyline(latlngs, { color: routeColorDA, weight: 10 }).addTo(map);
    } catch (error) {
      console.error(error.message);
    }
  }

  function setPolylineColor(color) {
    map.eachLayer(function (layer) {
      if (layer instanceof L.Polyline) {
        routeColorDA = color;
        layer.setStyle({ color: routeColorDA });
      }
    });
  }
  function setAndUpdateDAMarkersOnMap(data) {
    planeMarker.setLatLng([data.Latitude, data.Longitude]);
  }