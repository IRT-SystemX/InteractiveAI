var criticalities = fetch('./shared/json_samples/criticalities.json')
  .then(response => response.json())
  .then(data => {
    criticalities = data.criticalities;
  })
  .catch(error => {
    console.error('Erreur lors de la lecture du fichier JSON :', error);
  });

var newCriticalityReady = true;

function fillTimeLine() {
    var data = "";
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4) {
            var cards = JSON.parse(this.responseText)
            for (var card = 0; card < cards.length; card++) {
                var criticality = cards[card].criticality;
                if (criticality == "HIGH" && newCriticalityReady){
                        newCriticalityReady = false;
                            document.getElementById("eventsForTimeLine").innerHTML = "";
                }
                var date = cards[card].date;
                var title = cards[card].title;
                var description = cards[card].description;
                var id_event = cards[card].id_event;
                var use_case = cards[card].use_case;
                var heure_event = time_format(new Date(date));
                cartToAdd = "<div hidden class='blocEvent' id='event" + card  + "'>" +
                "<div class='bloc_title'" + "style = 'width: 185px;position:absolute;z-index: 2;height: 35px;background-color:"+ criticalities[use_case].color[criticality] + 
                ";border: 1px solid " + criticalities[use_case].color[criticality] + "' event_id='"+ id_event + "'" +
                " id='title" + card + "'>" + title + "</div>" + "<div class='timeline'>" +
                "<div class='timeline-line'><div class 'timeline-hour' style='left: 0;'></div><div class='timeline-hour' style='left: 25%;'></div>" +
                "<div class='timeline-hour' style='left: 50%;'></div><div class='timeline-hour' style='left: 75%;'></div><div class='timeline-hour' style='right: 0;'></div></div>" +
                "<div class='timeline-point' id='timeline-point" + card + "' style='left: calc(60.5556% - 4px);'>" + heure_event + criticalities[use_case].icon[criticality] + "</div>" +
                "<div class='timeline-highlight' id='timeline-highlight" + card + "' style='position:absolute;color: " + criticalities[use_case].color[criticality] + "'></div></div>";
                    document.getElementById("eventsForTimeLine").innerHTML += cartToAdd;
                    positionnerPointSurTimeline(heure_event, card);
                    getCardForTimeline(id_event,card);
  
            }
            
        }
    });
    xhr.open("GET", host + "/cab_event/api/v1/events"+"?time="+new Date().getTime());
    // xhr.open("GET", "./shared/json_samples/events.json");
    xhr.setRequestHeader("Authorization", "Bearer "+ token);
    xhr.send(data);
}


function getCardForTimeline(id_event,card){
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
            // document.getElementById("event"+card).setAttribute("onclick","acknowledgeEvent('" + uid + "','" + card + "')");
            try {
                document.getElementById("event"+card).hidden=false;
            } catch (error) {
                console.log("Unknown element")
            }
        }else{
            // document.getElementById("event"+card).innerHTML = ""
            document.getElementById("event"+card).remove();
            console.log("suppression de l'event  " + card)
        }
    }
    });

    xhr.open("GET", host + "/cards/cards/" + selectedUseCase.toLowerCase() + "Process."+id_event);
    xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
    xhr.setRequestHeader("Authorization", "Bearer " + token);
    
xhr.onloadend = function() {
    if(xhr.status == 404) 
        try {
        document.getElementById("event"+card).remove();
            
        } catch (error) {
            console.log("already removed")
        }

}
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




function initTimeLine() {
    console.info("TIMELINE : ", "Ready");
    document.getElementById("tl-container-home").hidden = false;
    fillTimeLine();
    updateGlobalCurrentTimeCursor();
    setInterval(() => {
            fillTimeLine();
            updateGlobalCurrentTimeCursor();
    }, 5000);
}

function updateGlobalCurrentTimeCursor() {
    var globalCurrentTimeCursor = document.querySelector('.global-current-time-cursor');
    var currentTimeDiv = document.getElementById('current-time');
    if (selectedUseCase == "RTE"){
        var currentTime = new Date();
    }else{
        var currentTime = new Date(dateCtx);
    }
    var totalMinutes = currentTime.getHours() * 60 + currentTime.getMinutes();
    var positionEnPourcentage = (totalMinutes / 1440) * 100;
    globalCurrentTimeCursor.style.left = "calc(" + positionEnPourcentage + "% - 4px)";
    currentTimeDiv.innerHTML = "<b>" + time_format(currentTime) + "</b>";
}

function positionnerPointSurTimeline(heure, timeline_id) {
    var positionObtenue = 0;

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
    var heureActuelle = new Date();
    var heureEvent = new Date();
    heureEvent.setHours(heures, minutes, 0, 0);
    if (heures < 0 || heures > 23 || minutes < 0 || minutes > 59) {
        console.error("Heure invalide. Assurez-vous que l'heure est entre 00:00 et 23:59.");
        return;
    }
    var positionEnPourcentage = ((heures * 60 + minutes) / 1440) * 100;
    point.style.left = "calc(" + positionEnPourcentage + "% - 4px)";
    timelineHighlightWidth = document.getElementById("timeline-point"+timeline_id).getBoundingClientRect().left - document.getElementsByClassName("global-current-time-cursor")[0].getBoundingClientRect().left;
    timelinePointMarginLeft = document.getElementById("timeline-point" + timeline_id).getBoundingClientRect().left;
    // // si l'heure actuelle est inférieure a la date de levenement 
        point.style.left = "calc(" + positionEnPourcentage + "% - 4px)";
        highlight.style.left = "calc(" + positionEnPourcentage + "% - 4px)";

        // if(heureActuelle < heureEvent){
            // highlight.style.left = document.getElementsByClassName("global-current-time-cursor")[0].getBoundingClientRect().left - document.getElementById("timeline-point" + timeline_id).offsetWidth + "px";
            // point.style.left = document.getElementsByClassName("global-current-time-cursor")[0].getBoundingClientRect().left - document.getElementById("timeline-point" + timeline_id).offsetWidth + "px";
            // positionObtenue++;
            if (Math.abs(timelineHighlightWidth)<300){
            highlight.style.width = Math.abs(timelineHighlightWidth) + "px";
            }
        // }else{
            // highlight.style.left = parseInt(timelinePointMarginLeft) + document.getElementById("timeline-point" + timeline_id).offsetWidth + "px";
            // point.style.left = parseInt(timelinePointMarginLeft) + document.getElementById("timeline-point" + timeline_id).offsetWidth + "px";
            // positionObtenue++;
        // }
    // }   
    
}
function time_format(d) {
    hours = format_two_digits(d.getHours());
    minutes = format_two_digits(d.getMinutes());
    return hours + ":" + minutes;
}

function format_two_digits(n) {
    return n < 10 ? '0' + n : n;
}