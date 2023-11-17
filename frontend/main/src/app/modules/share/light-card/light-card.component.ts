/* Copyright (c) 2018-2022, RTE (http://www.rte-france.com)
 * See AUTHORS.txt
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 * SPDX-License-Identifier: MPL-2.0
 * This file is part of the OperatorFabric project.
 */

import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { LightCard } from '@ofModel/light-card.model';
import { Router } from '@angular/router';
import { selectCurrentUrl } from '@ofStore/selectors/router.selectors';
import { Store } from '@ngrx/store';
import { AppState } from '@ofStore/index';
import { takeUntil } from 'rxjs/operators';
import { Observable, Subject } from 'rxjs';
import { ConfigService } from '@ofServices/config.service';
import { AppService, PageType } from '@ofServices/app.service';
import { EntitiesService } from '@ofServices/entities.service';
import { ProcessesService } from '@ofServices/processes.service';
import { UserPreferencesService } from '@ofServices/user-preference.service';
import { DisplayContext } from '@ofModel/templateGateway.model';
import { GroupedCardsService } from '@ofServices/grouped-cards.service';
import { TypeOfStateEnum } from '@ofModel/processes.model';
import { SoundNotificationService } from '@ofServices/sound-notification.service';
import { DateTimeFormatterService } from '@ofServices/date-time-formatter.service';
import { MapService } from '@ofServices/map.service';
import $, { get } from "jquery";
import Swal from 'sweetalert2/dist/sweetalert2.js';


@Component({
    selector: 'of-light-card',
    templateUrl: './light-card.component.html',
    styleUrls: ['./light-card.component.scss']
})
export class LightCardComponent implements OnInit, OnDestroy {
    @Input() public open = false;
    @Input() public groupedCardOpen = false;
    @Input() public selection: Observable<string>;
    @Input() public lightCard: LightCard;
    @Input() public displayUnreadIcon = true;
    @Input() displayContext: any = DisplayContext.REALTIME;
    @Input() lightCardDisplayedInMapComponent = false;

    currentPath: any;
    protected _i18nPrefix: string;
    dateToDisplay: string;
    fromEntity = null;
    showExpiredIcon = true;
    showExpiredLabel = true;
    expiredLabel = 'feed.lttdFinished';

    showGroupedCardsIcon = false;
    groupedCardsVisible = true;
    hasGeoLocation;
    isGeoMapEnabled;
    rteUrl = "/cabcontext/api/v1/contexts";
    token = window.localStorage.token;
    emergencyClicked = false;
    jsonEventObject;
    jsonContextObject;
    host = "";
    bypassCondition = false;


    private ngUnsubscribe: Subject<void> = new Subject<void>();

    constructor(
        private router: Router,
        private store: Store<AppState>,
        private dateTimeFormatter: DateTimeFormatterService,
        private configService: ConfigService,
        private _appService: AppService,
        private entitiesService: EntitiesService,
        private processesService: ProcessesService,
        private userPreferencesService: UserPreferencesService,
        private groupedCardsService: GroupedCardsService,
        private soundNotificationService: SoundNotificationService,
        private mapService: MapService
    ) { }

    ngOnInit() {
        this._i18nPrefix = `${this.lightCard.process}.${this.lightCard.processVersion}.`;
        this.store
            .select(selectCurrentUrl)
            .pipe(takeUntil(this.ngUnsubscribe))
            .subscribe((url) => {
                if (url) {
                    const urlParts = url.split('/');
                    this.currentPath = urlParts[1];
                }
            });
        this.computeFromEntity();
        this.computeDisplayedDate();
        this.computeLttdParams();
        this.computeGroupedCardsIcon();
        this.hasGeoLocation =
            this.lightCard.wktGeometry === undefined ||
                this.lightCard.wktGeometry == null ||
                this.lightCard.wktGeometry.length <= 0
                ? false
                : true;
        this.isGeoMapEnabled = this.configService.getConfigValue('feed.geomap.enableMap', false);
    }

    computeLttdParams() {
        this.processesService
            .queryProcess(this.lightCard.process, this.lightCard.processVersion)
            .subscribe((process) => {
                const state = process.extractState(this.lightCard);
                if (state.type === TypeOfStateEnum.FINISHED) {
                    this.showExpiredIcon = false;
                    this.showExpiredLabel = false;
                } else if (!!state.response) {
                    this.showExpiredIcon = false;
                    this.expiredLabel = 'feed.responsesClosed';
                }
            });
    }

    computeFromEntity() {
        if (this.lightCard.publisherType === 'ENTITY')
            this.fromEntity = this.entitiesService.getEntityName(this.lightCard.publisher);
        else this.fromEntity = null;
    }

    computeDisplayedDate() {
        switch (this.configService.getConfigValue('feed.card.time.display', 'BUSINESS')) {
            case 'NONE':
                this.dateToDisplay = '';
                break;
            case 'LTTD':
                this.dateToDisplay = this.handleDate(this.lightCard.lttd);
                break;
            case 'PUBLICATION':
                this.dateToDisplay = this.handleDate(this.lightCard.publishDate);
                break;
            case 'BUSINESS_START':
                this.dateToDisplay = this.handleDate(this.lightCard.startDate);
                break;
            default:
                this.dateToDisplay = `${this.handleDate(this.lightCard.startDate)} - ${this.handleDate(
                    this.lightCard.endDate
                )}`;
        }
    }

    private computeGroupedCardsIcon() {
        this.showGroupedCardsIcon = this.groupedCardsService.isParentGroupCard(this.lightCard);
    }

    getGroupedChildCards() {
        return this.groupedCardsService.getChildCardsByTags(this.lightCard.tags);
    }

    handleDate(timeStamp: number): string {
        return this.dateTimeFormatter.getFormattedDateAndTimeFromEpochDate(timeStamp);
    }
    public hideAllSynops(){
        var synops = ['STATUS','ECS','ELEC','FUEL','HYD','BLEED','TEST','ENGINE'];
        for (var synop=0;synop<synops.length;synop++){
          try {
            document.getElementById(synops[synop]).hidden= true;
          } catch (error) {
            console.log("unknown synop element")
          }
          try {
            document.getElementById(synops[synop]+"_nominal").hidden= true;
          } catch (error) {
            console.log("unknown synop nominal element")
          }
        }
      }
      public getRecommandationDA(title){
        var recoResponse;
        var data = JSON.stringify({
          "event": {
            "event_type": title
          }
        });
        var xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.addEventListener("readystatechange", function() {
          if(this.readyState === 4) {
            document.getElementById("da_block_request").innerHTML = "";
            document.getElementById("da_block_request").innerHTML += "Procedure <hr>"
            recoResponse = JSON.parse(this.responseText);
            Object.keys(recoResponse.da_recommendation.Procedure).forEach(function(k){
                document.getElementById("da_block_request").hidden = false;
                document.getElementById("da_block_request").innerHTML += recoResponse.da_recommendation.Procedure[k].TaskIndex + ' - ' +recoResponse.da_recommendation.Procedure[k].TaskText + '<hr>';
          });
    
          }
        });
        xhr.open("POST", this.host + "/cab_recommendation/api/v1/recommendation");
        // xhr.open("POST", "http://192.168.211.95:3200/cab_recommendation/api/v1/recommendation");
        xhr.setRequestHeader("Authorization", "Bearer "+ window.localStorage.token);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(data);
      }
      public getContextRTE(){
        var xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        var that = this;
        xhr.addEventListener("readystatechange", function() {
        if(this.readyState === 4) {
            Swal.hideLoading();
            Swal.close()
            that.jsonContextObject = JSON.parse(this.responseText);
            if(document.getElementById("rte_assist_nominal").hidden){
                that.getRecommandationRTE();
            }
        }
        });
        xhr.open("GET", this.host + "/cabcontext/api/v1/contexts");
        xhr.setRequestHeader("Authorization", "Bearer " + window.localStorage.token);
        xhr.send();
        
      }
      public getContextSNCF(){
        var xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        var that = this;
        xhr.addEventListener("readystatechange", function() {
        if(this.readyState === 4) {
            Swal.hideLoading();
            Swal.close()
            that.jsonContextObject = JSON.parse(this.responseText);
        }
        });
        xhr.open("GET", this.host + "/cabcontext/api/v1/contexts");
        xhr.setRequestHeader("Authorization", "Bearer " + window.localStorage.token);
        xhr.send();
        
      }

        public getCardProcess(){
            this.getContextRTE();
            var cards = document.getElementsByClassName("card");
            for (var card = 0; card < cards.length; card++) {
                if (cards[card].classList.contains("light-card-detail-selected")){
                this.getCard(cards[card].getAttribute("data-urlid"));
                }
              }
              
      }

    public getCard(id_card) {
      if (id_card != null){
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open("GET", this.host + "/cards/cards/"+id_card,false);
        xmlHttp.setRequestHeader("Authorization","Bearer "+ window.localStorage.token);
        xmlHttp.send(null);
        var response = JSON.parse(xmlHttp.responseText);
        var eventAttributes = response.card.data.metadata;
        console.log(eventAttributes);
        this.jsonEventObject = eventAttributes;
        this.jsonEventObject.event_id = id_card;
        console.log(this.jsonEventObject);
      }
    };

    public getRecommandationRTE(){
        console.log('getRecommandationRTE')
        document.getElementById('rte_assist').innerHTML = "";
        var bodyHTML;
        var xhr = new XMLHttpRequest();
        var lightCardObject = this;
        xhr.withCredentials = true;
        xhr.addEventListener("readystatechange", function() {
          if(this.readyState === 4) {
            Swal.hideLoading();
            document.body.style.cursor = 'unset';
            console.log(JSON.parse(this.responseText))
             var recosRTE = JSON.parse(this.responseText);
             for (var reco=0;reco<recosRTE.length;reco++){
                var description = recosRTE[reco].description;
                var agent_type = recosRTE[reco].agent_type;
                var title = recosRTE[reco].title;
                var actions = recosRTE[reco].actions;
                sessionStorage.setItem("actions"+"["+ reco + "]", JSON.stringify(actions[0]));
                bodyHTML = "<div><span class='rtePrd'><b onclick ='"+ 'showDesc(' + reco + ')' + " '>" + title + "</b></span><br>" + '<button onclick="applyRecommandation(' +reco+ ')"' + 'class="rteBtn">Appliquer</button><hr>';
                bodyHTML += "<span id='descriptionRTE" + reco + "' hidden>" + description + '</span>';
                document.getElementById('rte_assist').innerHTML += bodyHTML;
             }
             Swal.hideLoading();
             Swal.close()

          }
        });
        xhr.open("POST", this.host + "/cab_recommendation/api/v1/recommendation");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.setRequestHeader("Authorization", "Bearer " + window.localStorage.token);
        
        var recommendationBody = 
          { context : this.jsonContextObject[0].data.observation,
            event : this.jsonEventObject
          }
        xhr.send(JSON.stringify(recommendationBody));
        }
    public getRecommandationSNCF(){
        console.log('getRecommandationSNCF')
        document.getElementById('sncf_assist').innerHTML = "";
        var bodyHTML;
        var xhr = new XMLHttpRequest();
        var lightCardObject = this;
        xhr.withCredentials = true;
        xhr.addEventListener("readystatechange", function() {
          if(this.readyState === 4) {
            Swal.hideLoading();
            document.body.style.cursor = 'unset';
            console.log(JSON.parse(this.responseText))
             var recos = JSON.parse(this.responseText);
             for (var reco=0;reco<recos.length;reco++){
                var description = recos[reco].description;
                var agent_type = recos[reco].agent_type;
                var title = recos[reco].title;
                var actions = recos[reco].actions;
                sessionStorage.setItem("actions"+"["+ reco + "]", JSON.stringify(actions[0]));
                bodyHTML = "<div><span class='rtePrd'><b onclick ='"+ 'showDesc(' + reco + ')' + " '>" + title + "</b></span><br>" + '<button onclick="applyRecommandation(' +reco+ ')"' + 'class="rteBtn">Appliquer</button><hr>';
                bodyHTML += "<span id='descriptionSNCF" + reco + "' hidden>" + description + '</span>';
                document.getElementById('sncf_assist').innerHTML += bodyHTML;
             }
             Swal.hideLoading();
             Swal.close()

          }
        });
        xhr.open("POST", this.host + "/cab_recommendation/api/v1/recommendation");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.setRequestHeader("Authorization", "Bearer " + window.localStorage.token);
        
        var recommendationBody = 
          { context : this.jsonContextObject[0].data,
            event : this.jsonEventObject
          }
          console.log(recommendationBody)
        xhr.send(JSON.stringify(recommendationBody));
        }
    public getRecommandationSNCFold(){
        document.getElementById('sncf_solution').innerHTML = "";
        var bodyHTML;
        var xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.addEventListener("readystatechange", function() {
          if(this.readyState === 4) {
            var recoSNCF = JSON.parse(this.responseText)[0].data;
            document.getElementById('sncf_solution').innerHTML += recoSNCF;
          }
        });
        // xhr.open("POST", "http://192.168.211.95:3200/cab_recommendation/api/v1/recommendation");
        xhr.open("POST", this.host + "/cab_recommendation/api/v1/recommendation");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.setRequestHeader("Authorization", "Bearer " + window.localStorage.token);
        
        var recommendationBody = 
          { context : this.jsonContextObject[0].data.observation,
            event : this.jsonEventObject
          }
        xhr.send(JSON.stringify(recommendationBody));
        }
    


    public getCardTitle($event) {
        this.hideAllSynops();
        Swal.hideLoading();
        Swal.close()


        $.ajaxSetup({
            headers:{
               'Authorization': " Bearer " + this.token
            }
         });
        if(window.location.host.includes("localhost")){
            this.rteUrl = "http://192.168.211.95:3200/cabcontext/api/v1/contexts";
            this.host = "http://192.168.211.95:3200";
          }

        if (document.getElementById("opfab-card-title").innerHTML.includes("Surcharge")) {
            $("#opfab-div-card-template-security").hide()
            $("#opfab-div-card-template-op").hide()
            $("#rte_assist").show()
            document.getElementById("nominal_assist").hidden = true;

            
           
                document.getElementById("rte_assist_nominal").hidden = false;

            $("#opfab-div-card-template").hide()
            $("#opfab-div-card-template-noparades").hide()
            $("#opfab-div-card-template-agent").hide()
            $.ajaxSetup({
                headers:{
                   'Authorization': " Bearer " + this.token
                }
             });
            $.get(this.rteUrl + "?time=" +  + new Date().getTime(), function (data) {
                $("#ctxImg").attr("src", "data:image/png;base64," + data[0].data.topology)
                $(".opfab-card-response-header").hide();
            });
        } else if (document.getElementById("opfab-card-title").innerHTML.includes("Risque sur aléa")) {
            $("#opfab-div-card-template-security").hide()
            $("#opfab-div-card-template-op").hide()
            $("#rte_assist").show()
            document.getElementById("nominal_assist").hidden = true;

            
            if(document.getElementById("rte_assist_nominal").hidden &&
             document.getElementById("rte_assist_nominal").getAttribute("assistnevertriggered") == "false"){
                // this.getCardProcess();
                // Décommenter cette ligne pour obtenir des recommandations pour les event de type anticipation
            }
            $("#opfab-div-card-template").hide()
            $("#opfab-div-card-template-noparades").hide()
            $("#opfab-div-card-template-agent").hide()
            $.get(this.rteUrl + "?time=" +  + new Date().getTime(), function (data) {
                $("#ctxImg").attr("src", "data:image/png;base64," + data[0].data.topology)
                $(".opfab-card-response-header").hide();
            });
            setTimeout(() => {
                Swal.hideLoading();
                Swal.close()
            }, 5000);
            $("#rte_assist").hide()
            $("#opfab-div-card-template-security").show()
            $("#opfab-div-card-template-op").hide()
            $("#opfab-div-card-template-alarm").hide()
            $("#opfab-div-card-template-noparades").hide()
            $("#opfab-div-card-template-agent").hide()
        }
        else if (document.getElementById("opfab-card-title").innerHTML.includes("Alerte Agent")) {
            $.ajaxSetup({
                headers:{
                   'Authorization': " Bearer " + this.token
                }
             });
            $.get(this.rteUrl + "?time=" +  + new Date().getTime(), function (data) {
                $("#ctxImg").attr("src", "data:image/png;base64," + data[0].data.topology)
                $(".opfab-card-response-header").hide();
            });
            $("#opfab-div-card-template-agent").show()
            $("#rte_assist").hide()
            $("#opfab-div-card-template-security").hide()
            $("#opfab-div-card-template-op").hide()
            $("#opfab-div-card-template-alarm").hide()
            $("#opfab-div-card-template-noparades").hide()
        
    }
          else if (document.getElementById("opfab-card-title").innerHTML.includes("Application")) {
            document.getElementById("nominal_assist").hidden = true;
            document.getElementById("orange_assist").hidden = false;
      }
          else if (document.getElementById("opfab-card-title").innerHTML.includes("Retour de ligne") || document.getElementById("opfab-card-title").innerHTML.includes("Retrait de ligne")) {
                      $.get(this.rteUrl + "?time=" +  + new Date().getTime(), function (data) {
                          $("#ctxImg").attr("src", "data:image/png;base64," + data[0].data.topology)
                          $(".opfab-card-response-header").hide();
                      });
                      $("#opfab-div-card-template").hide()
                      $("#opfab-div-card-template-op").show()
                      $("#opfab-div-card-template-security").hide()
                      $("#opfab-div-card-template-alarm").hide()
                      $("#opfab-div-card-template-noparades").hide()
                      $("#opfab-div-card-template-agent").hide()
                  }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("FAULT")) {
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            document.getElementById("high_procedure").hidden = false;
            document.getElementById("pdv_da").hidden = true;
        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("ENG1")) {
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            document.getElementById("high_procedure").hidden = true;
            document.getElementById("pdv_da").hidden = true;
            document.getElementById("da_block_request").hidden = true;
            this.getRecommandationDA(document.getElementById("opfab-card-title").innerText);
            document.getElementById("ELEC_nominal").setAttribute("src",document.getElementById("ELEC").getAttribute("src"));
            document.getElementById("ENGINE_nominal").setAttribute("src",document.getElementById("ENGINE").getAttribute("src"));
            document.getElementById("HYD_nominal").setAttribute("src",document.getElementById("HYD").getAttribute("src"));
            document.getElementById("FUEL_nominal").setAttribute("src",document.getElementById("FUEL").getAttribute("src"));
            document.getElementById("ELEC_nominal").hidden = false;

        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("Panne")) {
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            document.getElementById("high_procedure").hidden = true;
            document.getElementById("pdv_da").hidden = true;
            document.getElementById("noevent_da").hidden = false;
        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("PRESS")) {
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            document.getElementById("high_procedure").hidden = true;
            document.getElementById("pdv_da").hidden = true;
            document.getElementById("ECS_nominal").setAttribute("src",document.getElementById("ECS").getAttribute("src"));
            document.getElementById("ECS").hidden = false;
            this.getEmergencyPlan();
        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("ELEC")) {
            document.getElementById("high_procedure").hidden = true;
            document.getElementById("pdv_da").hidden = true;
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            document.getElementById("ELEC_nominal").setAttribute("src",document.getElementById("ELEC").getAttribute("src"));
            document.getElementById("ELEC_nominal").hidden = false;
        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("ENGINE")) {
            document.getElementById("high_procedure").hidden = true;
            document.getElementById("pdv_da").hidden = true;
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            document.getElementById("ENGINE_nominal").setAttribute("src",document.getElementById("ENGINE").getAttribute("src"));
            document.getElementById("ENGINE_nominal").hidden = false;
        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("FUEL")) {
            document.getElementById("high_procedure").hidden = true;
            document.getElementById("pdv_da").hidden = true;
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            document.getElementById("FUEL_nominal").setAttribute("src",document.getElementById("FUEL").getAttribute("src"));
            document.getElementById("FUEL_nominal").hidden = false;
        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("HYD")) {
            document.getElementById("high_procedure").hidden = true;
            document.getElementById("pdv_da").hidden = true;
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            document.getElementById("HYD_nominal").setAttribute("src",document.getElementById("HYD").getAttribute("src"));
            document.getElementById("HYD_nominal").hidden = false;
        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("Malaise")) {
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            console.log(this)
            document.getElementById("opfab-card-title").setAttribute("onclick","askCab()");
            if(document.getElementById("sncf_assist_nominal").getAttribute("triggered") == "false"){
              document.getElementById("sncf_assist_nominal").hidden = true;
              document.getElementById("sncf_assist_nominal").setAttribute("triggered","true");
            }
            document.getElementById("nominal_assist").hidden = true;

        }
         else if (document.getElementById("opfab-card-title").innerHTML.includes("Signal alarme") || document.getElementById("opfab-card-title").innerHTML.includes("Event")) {
            $(".opfab-card-response-header").hide();
            $("#opfab-card-detail-footer").hide();
            $("#rte_assist").hide()
            var cardDesc = document.getElementsByClassName("sncf-light-card-selected")[0].getElementsByTagName("span")[2].innerText;
            document.getElementById("sncf_incident_infos").innerHTML 
            = 
            '<div class="sncf_incidents" id="incidents">' 
            + '<b>Fiche Evenement</b><br>'
            + '<img src = "/assets/images/map.png">' + "TGV n° : " + cardDesc.substring(0, cardDesc.indexOf(' ')) +"<br>"
            + '<img src = "/assets/images/information.png">' + document.getElementById("opfab-card-title").innerText + "<br>"
            + '<img src = "/assets/images/time.png">' +new Intl.DateTimeFormat('fr-FR', { dateStyle: 'full', timeStyle: 'short', timeZone: 'Europe/Paris' }).format(new Date()) + "<br>"
            + '<img src = "/assets/images/warning.png">' + document.getElementsByClassName("sncf-light-card-selected")[0].getElementsByTagName("span")[1].innerText.replace("Routine ","Gravité Mineure")  
            + "</div>"
            + '<div class="sncf_incidents" id="sncf_dependances">'
            + '<b>Dépendances</b><br>'
            + 'Aucune dépendance à afficher'
            + '</div>';
            document.getElementById("incident").classList.add("toBlink");
        }

    }
    public getEmergencyPlan() {
        if (!this.emergencyClicked){
          document.getElementById("noevent_da").hidden=true;
          document.getElementById("da_block_request").innerHTML = "";
          var xmlHttp = new XMLHttpRequest();
          xmlHttp.open("GET", this.host + "./assets/emergency_procedures_short.json", false);
          // xmlHttp.open("GET", "/cabcontext/api/v1/contexts?time=" + new Date().getTime(), false);
          xmlHttp.setRequestHeader("Authorization","Bearer "+this.token);
          xmlHttp.send(null);
          var response = JSON.parse(xmlHttp.responseText);
          Object.keys(response.procedure).forEach(function(key) {
            var blockIndex = response.procedure[key].block.block_index;
            var blockName = response.procedure[key].block.block_name;
            var blockTask = response.procedure[key].block.toExecute;
            document.getElementById("da_block_request").innerHTML+= "<button class='assist_da_btn'><b>" + blockName + "</b></button><br>"
            Object.keys(blockTask).forEach(function(key) {
              console.log(blockTask[key])
            document.getElementById("da_block_request").innerHTML+= "<span>"  + blockTask[key].index + " - " + blockTask[key].type +" "+  blockTask[key].content + "</span><br>"
            });
          });
            document.getElementById("da_block_request").innerHTML+= "<hr><span><b>Active limitations</b></span><br>";
            document.getElementById("da_block_request").innerHTML+= "<span> Speed MIN - " + response.maxSpeed + "</span><br>";
            document.getElementById("da_block_request").innerHTML+= "<span> Speed MAX - " + response.minSpeed + "</span><br>";
            document.getElementById("assistOpTitle").style.overflowY = "scroll";
            this.emergencyClicked = true;
      }else{
        document.getElementById("da_block_request").hidden = true;
        document.getElementById("assistOpTitle").style.overflowY = "hidden";
      }
      };
    public select($event) {
        Swal.showLoading();
        var element = $event.srcElement;
        while (element && !element.classList.contains('card')) {
          console.log((element));
          element = element.parentElement;
      }
      // Vérifie si l'élément avec la classe 'card' a été trouvé
      if (element && element.classList.contains('card')) {
        console.log(element)
          element.classList.add('hasBeenRead');
          element.querySelector(".card-title").classList.add("hasBeenRead")
      }
        $event.stopPropagation();
        // Fix for https://github.com/opfab/operatorfabric-core/issues/2994
        this.soundNotificationService.clearOutstandingNotifications();
        if (this.open && this.groupedCardsService.isParentGroupCard(this.lightCard)) {
            this.groupedCardsVisible = !this.groupedCardsVisible;
        } else {
            this.groupedCardsVisible = true;
        }
        if (this.displayContext != DisplayContext.PREVIEW)
            this.router.navigate(['/' + this.currentPath, 'cards', this.lightCard.id]);
        setTimeout(() => {
            this.getCardTitle($event)
        }, 1000);
    }


    get i18nPrefix(): string {
        return this._i18nPrefix;
    }

    isArchivePageType(): boolean {
        return this._appService.pageType === PageType.ARCHIVE;
    }

    ngOnDestroy(): void {
        this.ngUnsubscribe.next();
        this.ngUnsubscribe.complete();
    }

    highlightOnMap(highlight: boolean) {
        if (this.isGeoMapEnabled) {
            this.mapService.highlightOnMap(highlight, this.lightCard);
        }
    }

    zoomToLocation($event) {
        $event.stopPropagation();
        // Fix for https://github.com/opfab/operatorfabric-core/issues/2994
        this.soundNotificationService.clearOutstandingNotifications();
        this.mapService.zoomToLocation(this.lightCard);
    }
}
