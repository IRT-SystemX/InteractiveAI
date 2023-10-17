function confirmExit() {
    Swal.fire({
        icon: 'question',
        title: 'Voulez vous vraiment vous déconnecter ?',
        showCancelButton: true,
        showConfirmButton: true,
        cancelButtonText: "Annuler",
        confirmButtonText: "Confirmer",
    }).then((result) => {
        if (result.isConfirmed) {
            document.body.style.cursor = 'wait';
            disconnectInProgress();
            acknowledgeAllCards();
        }
    })
}

function confirmAction(reco) {
    Swal.fire({
        icon: 'question',
        title: 'Voulez vous vraiment appliquer ?',
        showCancelButton: true,
        showConfirmButton: true,
        cancelButtonText: "Annuler",
        confirmButtonText: "Confirmer",
    }).then((result) => {
        if (result.isConfirmed) {
            traceInHistory("AWARD", authorizedUseCase, {});
            applyRecommandationFinal(reco);
        }
    })
}
function swalReco() {
    Swal.fire({
        icon: 'info',
        title: 'Application en cours',
        showConfirmButton: false,
    })
}
function disconnectInProgress() {
    Swal.fire({
        title: 'Déconnexion en cours',
        showConfirmButton: false,
    })
}
function swalRecoSuccess() {
    Swal.fire({
        icon: 'success',
        title: 'Recommandation Appliquée',
        showConfirmButton: false,
        timer: 4500
    })
}
function swalAskCab() {
    Swal.fire({
        title: 'Choisir un event',
        showConfirmButton: true,
    })
}
function swalRecoError(err) {
    Swal.fire({
        icon: 'error',
        title: 'Erreur serveur (Code : ' + err + ')',
        text: "Impossible d'appliquer la recommandation",
        showConfirmButton: true,
        confirmButtonText: "Ok"
    })
}

function showDesc(desc) {
    for (var desc_check = 0; desc_check < 3; desc_check++) {
        if (desc_check != desc) {
            document.getElementById('descriptionRTE' + desc_check).hidden = true;
        }
    }
    document.getElementById('descriptionRTE' + desc).hidden = false;
}
function showDescSNCF(desc) {
    for (var desc_check = 0; desc_check < 3; desc_check++) {
        try {
            if (desc_check != desc) {
                document.getElementById('descriptionSNCF' + desc_check).hidden = true;
            }
        } catch (error) {
            
        }
    }
    document.getElementById('descriptionSNCF' + desc).hidden = false;
}
function displaySwal() {
    Swal.fire({
        html: '<span style="font-size:20px">Paramétrage service corrélation</span><br>'
            + '<div id="box_methode_calcul"><b>Choix de la méthode de calcul</b>'
            + '<div style="width:100%;"><br><form>'
            + '<input name="choice" type="radio"><label style="width:70%">Méthode 1</label>' + '<img class="reduced" src="./assets/images/!.png">' + '<br><hr>'
            + '<input name="choice" type="radio"><label style="width:70%">Méthode 2</label>' + '<img class="reduced" src="./assets/images/!.png"><br>'
            + '</form></div><br>'
            + '<b>Choix des KPIs</b>'
            + '<div style="width:100%;"><br><form>'
            + '<input name="choiceKPI" type="radio"><label style="width:70%">Nombre de pages lentes</label>' + '<img class="reduced" src="./assets/images/!.png">' + '<br><hr>'
            + '<input name="choiceKPI" type="radio"><label style="width:70%">Temps de réponse</label>' + '<img class="reduced" src="./assets/images/!.png"><hr>'
            + '<input name="choiceKPI" type="radio"><label style="width:70%">Nombre de requêtes</label>' + '<img class="reduced" src="./assets/images/!.png">' + '<br><hr>'
            + '<input name="choiceKPI" type="radio"><label style="width:70%">Nombre d\'erreurs 4xx-5xx</label>' + '<img class="reduced" src="./assets/images/!.png"><hr>'
            + '<input name="choiceKPI" type="radio"><label style="width:70%">Taux de pages lentes</label>' + '<img class="reduced" src="./assets/images/!.png"><hr>'
            + '<input name="choiceKPI" type="radio"><label style="width:70%">Taux d\'érreurs</label>' + '<img class="reduced" src="./assets/images/!.png"><hr>'
            + '</form></div>'
            + '</div>'
            + '<div id="orangeTimeSelector">'
            + '<b>Fenêtre de temps</b>'
            + '<br>'
            + '<input type="range" id="slider" name="temp" list="values" />'
            + '<datalist id="values">'
            + '<option value="15" label="15mn"></option>'
            + '<option value="60" label="1h"></option>'
            + '<option value="120" label="2h"></option>'
            + '<option value="180" label="3h"></option>'
            + '<option value="240" label="4h"></option>'
            + '<option value="300" label="5h"></option>'
            + '</datalist>'
            + '</div>'
            + '<button onclick="Swal.close();getCorrelations()">Calculer Corrélation</button>',
        showConfirmButton: false
    })
}