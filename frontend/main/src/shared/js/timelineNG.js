var criticalities = fetch('./shared/json_samples/criticalities.json')
  .then(response => response.json())
  .then(data => {
    criticalities = data.criticalities;
  })
  .catch(error => {
    console.error('Erreur lors de la lecture du fichier JSON :', error);
  });

var newCriticalityReady = true;
var events;

function fillTimeLine() {
    var data = "";
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4) {
            var cards = JSON.parse(this.responseText)
            for (var card = 0; card < cards.length; card++) {
                var criticality = cards[card].criticality;
                var date = cards[card].start_date;
                var end_date = cards[card].end_date;
                var title = cards[card].title;
                var description = cards[card].description;
                var id_event = cards[card].id_event;
                var use_case = cards[card].use_case;
                var heure_event = time_format(new Date(date));
                var heure_event_fin = end_date ? time_format(new Date(end_date)) : null;
                var id_bloc_event = document.getElementById("event" + card)

                    if(document.getElementById("opfab-feed-light-card-" + selectedUseCase.toLowerCase() + "Process-" + id_event) 
                    && !document.getElementById("event"+card)){
                        cardToAdd = "<div hidden class='blocEvent' id='event" + card  + "'>" +
                        "<div class='bloc_title'" + "style = 'width: 185px;position:absolute;z-index: 2;height: 40px;background-color:var(--opfab-bgcolor);color:"+ criticalities[use_case].color[criticality] + 
                        ";border: 1px solid " + criticalities[use_case].color[criticality] + ';box-shadow: -4px 0px 0px ' + criticalities[use_case].color[criticality] + "' event_id='"+ id_event + "'" +
                        " id='title" + card + "'>" + "<div>"+title +"</div>" + "<div style='position:absolute;right:0px;'>"+criticalities[use_case].icon.timeline[criticality] + "</div>" + "</div>" + "<div class='timeline'>" +
                        "<div class='timeline-line'><d<div class='timeline-hour' style='left: 0;'></div><div class='timeline-hour' style='left: 25%;'></div>" +
                        "<div class='timeline-hour' style='left: 50%;'></div><div class='timeline-hour' style='left: 75%;'></div><div class='timeline-hour' style='right: 0;'></div></div>" +
                        "<div class='timeline-point tl-point' id='timeline-point" + card + "'>" 
                        + "<span class='tl_hour'>" + heure_event + "</span>" 
                        + criticalities[use_case].icon[criticality] + "</div>" +
                        "<div class='timeline-point-end tl-point' id='timeline-point-end" + card + "'>" + (heure_event_fin !== null ? "<span class='tl_hour'>" + heure_event_fin + "</span><img src='assets/images/done.png'>" : "") + "</div>" +
                        "<div class='timeline-highlight' id='timeline-highlight" + card + "' style='position:absolute;color: " + criticalities[use_case].color[criticality] + "' hidden></div></div>";
                        document.getElementById("eventsForTimeLine").innerHTML += cardToAdd;
                        positionnerPointSurTimeline(heure_event, card, heure_event_fin)
                        getCardForTimeline(id_event,card);
                    }
            }
            events = document.getElementsByClassName("blocEvent")
                for (var event = 0; event<events.length;event++){
                    var id_image_top_event = document.getElementById("event" + [event] + "icon")
                    if (!document.getElementsByClassName("blocEvent")[event].hidden && !id_image_top_event){
                    document.getElementById("timeline-line").innerHTML += "<img id='event" + [event] + "icon'>";
                    document.getElementById("event" + [event] + "icon").src = document.getElementById("timeline-point"+document.getElementsByClassName("blocEvent")[event].id.match(/\d+/)[0]).querySelector("img").src
                    document.getElementById("event" + [event] + "icon").style.left = document.getElementsByClassName("timeline-point")[event].style.left
                    document.getElementById("event" + [event] + "icon").style.position = "absolute"
                    document.getElementById("event" + [event] + "icon").style.marginTop = "-25px"
                    document.getElementById("event" + [event] + "icon").style.marginLeft = "-5px"
                    document.getElementById("event" + [event] + "icon").setAttribute("card_id_point",document.getElementsByClassName("blocEvent")[event].id.match(/\d+/)[0])
                    
                    if(heure_event_fin){
                        document.getElementById("timeline-line").innerHTML += "<img id='event" + [event] + "icon_end'>"
                        document.getElementById("event" + [event] + "icon_end").src = document.getElementById("timeline-point-end"+document.getElementsByClassName("blocEvent")[event].id.match(/\d+/)[0]).querySelector("img").src
                        document.getElementById("event" + [event] + "icon_end").style.left = document.getElementById("timeline-point-end"+document.getElementsByClassName("blocEvent")[event].id.match(/\d+/)[0]).style.left
                        document.getElementById("event" + [event] + "icon_end").style.position = "absolute"
                        document.getElementById("event" + [event] + "icon_end").style.marginTop = "-25px"
                        document.getElementById("event" + [event] + "icon_end").style.marginLeft = "-12px"
                        document.getElementById("event" + [event] + "icon_end").setAttribute("card_id_point_end",document.getElementsByClassName("blocEvent")[event].id.match(/\d+/)[0])
                    }

                }
                }
        }
    });
    xhr.open("GET", host + "/cab_event/api/v1/events"+"?time="+new Date().getTime());
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
            // document.getElementById("event"+card).setAttribute("onclick","acknowledgeEvent('" + uid + "','" + card + "')");
            // cards[card].innerHTML += 
            try {
                cardName = 'opfab-feed-light-card-' + selectedUseCase.toLowerCase() + 'Process-' + document.querySelector('#event'+card+' [event_id]').getAttribute("event_id")
                if (document.getElementById(cardName).querySelector(".imgBin") == null) {
                    var trashIconSrc = selectedUseCase !== "DA" ? "assets/images/trashIcon.svg" : "assets/images/trashIconDA.svg";
                    document.getElementById(cardName).innerHTML += '<img class="imgBin" src="' + trashIconSrc + '" width="10%" onclick="event.stopPropagation();acknowledgeEvent(\'' + uid + '\', \'' + card + '\', \'' + id_event + '\')">';
                }
            } catch (error) {
                console.log("Cant find matching id "+ cardName);
                
            }
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

function acknowledgeEvent(uid,card,id_event){
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    var data = JSON.stringify([
        selectedUseCase
      ]);
    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4 && this.status == 201) {
            document.getElementById("event"+card).style.display = 'none';
            document.getElementById("event"+card).remove();
            document.getElementById("opfab-feed-light-card-" + selectedUseCase.toLocaleLowerCase() + "Process-" + id_event).remove();
            document.querySelector('img[card_id_point="' + card + '"]').remove();
            document.querySelector('img[card_id_point_end="' + card + '"]').remove();
        }
    });
    xhr.open("POST", "http://192.168.211.95:2002/cardspub/cards/userAcknowledgement/" + uid);
    xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", "Bearer "+ token);

    xhr.send(data);
    
}




function initTimeLine() {
    console.info("TIMELINE : ", "Ready");
    document.getElementById("tl-container-home").hidden = false;
    updateGlobalCurrentTimeCursor();
    setInterval(() => {
            fillTimeLine();
            updateHighlights();
            document.getElementById("eventsForTimeLine").hidden = false
            updateGlobalCurrentTimeCursor();
    }, 5000);
}

function updateGlobalCurrentTimeCursor() {
    var globalCurrentTimeCursor = document.querySelector('.global-current-time-cursor');
    var currentTimeDiv = document.getElementById('current-time');
    if (selectedUseCase == "RTE" ||selectedUseCase == "ORANGE" ){
        var currentTime = new Date();
    }else{
        var currentTime = new Date(dateCtx);
    }
    var totalMinutes = currentTime.getHours() * 60 + currentTime.getMinutes();
    var positionEnPourcentage = (totalMinutes / 1440) * 100;
    globalCurrentTimeCursor.style.left = "calc(" + positionEnPourcentage + "% - 4px)";
    currentTimeDiv.innerHTML = "<b>" + time_format(currentTime) + "</b>";
}

function positionnerPointSurTimeline(heure, timeline_id, end_date) {

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
}

function updateHighlights(){
    var highlights = document.querySelectorAll(".timeline-highlight")
    for(var highlight=0;highlight<highlights.length;highlight++){
        var timeline_id = highlights[highlight].id.match(/\d+/)[0]
        var heure = highlights[highlight].parentElement.querySelector("#timeline-point"+timeline_id).outerText
        var heureMinutes = heure.split(':');
        var end_date = highlights[highlight].parentElement.querySelector("#timeline-point-end"+timeline_id).outerText
        var heures = parseInt(heureMinutes[0]);
        var minutes = parseInt(heureMinutes[1]);
        var positionEnPourcentage = ((heures * 60 + minutes) / 1440) * 100;
        var timelineHighlightWidth = document.getElementById("timeline-point"+timeline_id).getBoundingClientRect().left - document.getElementsByClassName("global-current-time-cursor")[0].getBoundingClientRect().left;
        highlights[highlight].style.left = "calc(" + positionEnPourcentage + "% - 4px)";
        highlights[highlight].hidden = false;
        if(end_date){
            positionnerPointFinDateEventSurTimeline(end_date,timeline_id)
            var end_timelineHighlightWidth = document.getElementById("timeline-point"+timeline_id).getBoundingClientRect().left - document.getElementById("timeline-point-end"+timeline_id).getBoundingClientRect().left;
            highlights[highlight].style.width = Math.abs(end_timelineHighlightWidth) + "px";
        }else{
            highlights[highlight].style.width = Math.abs(timelineHighlightWidth) + "px";
        }
        if (document.getElementById("eventsForTimeLine").innerHTML == ""){
            document.querySelectorAll('img[id^="event"][id$="icon"], img[id^="event"][id$="icon_end"]');
        }
}
}
function positionnerPointFinDateEventSurTimeline(heure, timeline_id) {

    var point = document.getElementById('timeline-point-end' + timeline_id);
    var heureRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
    if (!heureRegex.test(heure)) {
        console.error("Format d'heure invalide. Utilisez le format HH:mm.");
        return;
    }
    var highlight = document.getElementById('timeline-highlight' + timeline_id);

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
    point.style.marginLeft = "-12px";
}
function time_format(d) {
    hours = format_two_digits(d.getHours());
    minutes = format_two_digits(d.getMinutes());
    return hours + ":" + minutes;
}

function format_two_digits(n) {
    return n < 10 ? '0' + n : n;
}