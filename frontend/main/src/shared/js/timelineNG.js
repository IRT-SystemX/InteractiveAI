var criticalities = fetch('./shared/json_samples/criticalities.json')
  .then(response => response.json())
  .then(data => {
    criticalities = data.criticalities;
  })
  .catch(error => {
    console.error('Erreur lors de la lecture du fichier JSON :', error);
  });

  
function initTimeLine() {
    console.info("TIMELINE : ", "Ready")
}

function fillTimeLine() {
    var data = "";
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4) {
            var cards = JSON.parse(this.responseText);
            var eventsForTimeLine = document.getElementById("eventsForTimeLine"); // Élément HTML cible

            for (var card = 0; card < cards.length; card++) {
                var criticality = cards[card].criticality;
                var date = cards[card].date;
                var title = cards[card].title;
                var description = cards[card].description;
                var id_event = cards[card].id_event;
                var use_case = cards[card].use_case;
                var heure_event = time_format(new Date(date));
                // var heure_event = "17:12";

                var htmlContent = "<div hidden class='blocEvent' id='event" + card + "' style='visibility:hidden'>" + 
                    "<div class='bloc_title'" + "style = 'background-color:"+ criticalities[use_case].color[criticality] + 
                    ";border: 1px solid " + criticalities[use_case].color[criticality] + "' event_id='"+ id_event + "'" +
                    " id='title" + card + "'>" + title + "</div>" + "<div class='timeline'>" +
                    "<div class='timeline-line'><div class='timeline-hour' style='left: 0;'></div><div class='timeline-hour' style='left: 25%;'></div>" +
                    "<div class='timeline-hour' style='left: 50%;'></div><div class='timeline-hour' style='left: 75%;'></div><div class='timeline-hour' style='right: 0;'></div></div>" +
                    "<div class='timeline-point' id='timeline-point" + card + "' style='left: calc(60.5556% - 4px);'>" + heure_event + criticalities[use_case].icon[criticality] + "</div>" +
                    "<div class='timeline-highlight' id='timeline-highlight" + card + "' style='width: 60.5556%;color: " + criticalities[use_case].color[criticality] + "'></div></div>";

                eventsForTimeLine.innerHTML += htmlContent;
                positionnerPointSurTimeline(heure_event, card);
                getCard(id_event, card);
            }

        }
    });

    xhr.open("GET", host + "/cab_event/api/v1/events");
    xhr.setRequestHeader("Authorization", "Bearer " + token);
    xhr.send(data);
}


function getCard(id_event,card){
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
    if(this.readyState === 4) {
        try {
            var data = JSON.parse(this.responseText);

        } catch (error) {
            return;
        }
        var uid = data.card.uid;
        var hasBeenAcknowledged = data.card.hasBeenAcknowledged;
        if(!hasBeenAcknowledged){
            document.getElementById("event"+card).setAttribute("onclick","acknowledgeEvent('" + uid + "','" + card + "')");
            document.getElementById("event"+card).style.visibility="unset";
            document.getElementById("event"+card).hidden=false;
        }else{
            document.getElementById("event"+card).innerHTML = ""
        }
    }
    });

    xhr.open("GET", host + "/cards/cards/" + selectedUseCase.toLowerCase() + "Process."+id_event);
    xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
    xhr.setRequestHeader("Authorization", "Bearer " + token);
    xhr.send(); 
}

function acknowledgeEvent(id_event,card){
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    var data = JSON.stringify([
        selectedUseCase
      ]);
    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4 && this.status == 201) {
            document.getElementById("event"+card).style.display = 'none';
        }
    });

    xhr.open("POST", "http://192.168.211.95:2002/cardspub/cards/userAcknowledgement/" + id_event);
    xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
  xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", "Bearer "+ token);

    xhr.send(data);
    
}


function positionnerPointSurTimeline(heure, timeline_id) {
    var point = document.getElementById('timeline-point' + timeline_id);
    var highlight = document.getElementById('timeline-highlight' + timeline_id);
    var heureRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
   
    if (!heureRegex.test(heure)) {
        console.error("Format d'heure invalide. Utilisez le format HH:mm.");
        return;
    }

    var heureMinutes = heure.split(':');
    var heures = parseInt(heureMinutes[0]);
    var minutes = parseInt(heureMinutes[1]);

    if (heures < 0 || heures > 23 || minutes < 0 || minutes > 59) {
        console.error("Heure invalide. Assurez-vous que l'heure est entre 00:00 et 23:59.");
        return;
    }

    var positionEnPourcentage = ((heures * 60 + minutes) / 1440) * 100;
    point.style.left = "calc(" + positionEnPourcentage + "% - 4px)";
    highlight.style.width = positionEnPourcentage + "%";
}
// ...

function initTimeLine() {
    console.info("TIMELINE : ", "Ready");
    setInterval(() => {
        fillTimeLine();
        updateGlobalCurrentTimeCursor();
    }, 5000);
}

// ...

function updateGlobalCurrentTimeCursor() {
    var globalCurrentTimeCursor = document.querySelector('.global-current-time-cursor');
    var currentTimeDiv = document.getElementById('current-time');
    var currentTime = new Date();
    var hours = currentTime.getHours();
    var minutes = currentTime.getMinutes();
    var totalMinutes = hours * 60 + minutes;
    currentTimeDiv.innerHTML = time_format(currentTime);
    var timelineWidth = document.querySelector('.timeline').offsetWidth;
    var cursorPosition = (totalMinutes / 1440) * timelineWidth; 
    globalCurrentTimeCursor.style.left = cursorPosition + 'px';
}

function time_format(d) {
    hours = format_two_digits(d.getHours());
    minutes = format_two_digits(d.getMinutes());
    return hours + ":" + minutes;
}

function format_two_digits(n) {
    return n < 10 ? '0' + n : n;
}