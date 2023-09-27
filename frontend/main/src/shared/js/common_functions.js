var targetObj = {};
var targetProxy = new Proxy(targetObj, {
    set: function (target, key, value) {
        if (key == "isAcknowledging" && value == false) {
            setTimeout(() => {
                localStorage.clear(); window.location.reload()
            }, "4000");

        }
        target[key] = value;
        return true;
    }
});
targetProxy.isAcknowledging = null;

function acknowledgeAllCards() {

    var cards = document.getElementsByClassName("card");
    targetProxy.isAcknowledging = true;
    for (var card = 0; card < cards.length; card++) {
        try {
            getCardToAknowledge(cards[card].attributes["data-urlid"].value.split(".")[1]);
        } catch (error) {
            console.log("ERROR = " + error)
        }
    }
    targetProxy.isAcknowledging = false;
}

function getCardToAknowledge(id_event) {
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4) {
            var data = JSON.parse(this.responseText);
            var uid = data.card.uid;
            console.log(uid);
            acknowledgeCard(uid);
        }
    });
    xhr.open("GET", host + "/cards/cards/" + selectedUseCase.toLocaleLowerCase() + "Process." + id_event);
    xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
    xhr.setRequestHeader("Authorization", "Bearer " + token);
    xhr.send();
}

function acknowledgeCard(uid) {
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    var data = JSON.stringify([
        selectedUseCase
    ]);
    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4 && this.status == 201) {
            console.info("CARDS", "card ack OK -> " + uid)
        }
    });

    xhr.open("POST", host + "/cardspub/cards/userAcknowledgement/" + uid);
    xhr.setRequestHeader("Accept", "application/json, text/plain, */*");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", "Bearer " + token);
    xhr.send(data);

}
