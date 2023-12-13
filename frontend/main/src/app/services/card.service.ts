/* Copyright (c) 2018-2022, RTE (http://www.rte-france.com)
 * See AUTHORS.txt
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 * SPDX-License-Identifier: MPL-2.0
 * This file is part of the OperatorFabric project.
 */

import {Injectable} from '@angular/core';
import {Observable, Subject} from 'rxjs';
import {CardOperation, CardOperationType} from '@ofModel/card-operation.model';
import {EventSourcePolyfill} from 'ng-event-source';
import {AuthenticationService} from './authentication/authentication.service';
import {Card, CardData, CardForPublishing, fromCardToLightCard} from '@ofModel/card.model';
import {HttpClient, HttpParams, HttpResponse} from '@angular/common/http';
import {environment} from '@env/environment';
import {GuidService} from '@ofServices/guid.service';
import {LightCard} from '@ofModel/light-card.model';
import {Page} from '@ofModel/page.model';
import {AppState} from '@ofStore/index';
import {Store} from '@ngrx/store';
import {
    CardSubscriptionClosedAction,
    CardSubscriptionOpenAction,
    UIReloadRequestedAction
} from '@ofActions/cards-subscription.actions';
import {catchError, map, takeUntil} from 'rxjs/operators';
import {RemoveLightCardAction} from '@ofActions/light-card.actions';
import {BusinessConfigChangeAction} from '@ofStore/actions/processes.actions';
import {UserConfigChangeAction} from '@ofStore/actions/user.actions';
import {LightCardsStoreService} from './lightcards/lightcards-store.service';
import {LoadCardAction} from '@ofStore/actions/card.actions';
import {I18n} from '@ofModel/i18n.model';
import {FilterService} from '@ofServices/lightcards/filter.service';
import {LogOption, OpfabLoggerService} from './logs/opfab-logger.service';
import packageInfo from '../../../package.json';
import {SoundNotificationService} from './sound-notification.service';
import $ from "jquery";
import {setStatus} from "shared/js/d3graph.js"

@Injectable({
    providedIn: 'root'
})
export class CardService {
    private static TWO_MINUTES = 120000;

    readonly cardOperationsUrl: string;
    readonly deleteCardSubscriptionUrl: string;
    readonly cardsUrl: string;
    readonly archivesUrl: string;
    readonly cardsPubUrl: string;
    readonly userCardReadUrl: string;
    readonly userCardUrl: string;
    private lastHeardBeatDate = 0;
    private firstSubscriptionInitDone = false;
    public initSubscription = new Subject<void>();
    private unsubscribe$: Subject<void> = new Subject<void>();
    public cardAlreadySet = false;
    public cardCount = 0;


    private startOfAlreadyLoadedPeriod: number;
    private endOfAlreadyLoadedPeriod: number;

    private selectedCardId: string = null;

    private receivedAcksSubject = new Subject<{cardUid: string; entitiesAcks: string[]}>();
    private receivedDisconnectedSubject = new Subject<boolean>();

    private subscriptionClosed = false;

    constructor(
        private httpClient: HttpClient,
        private guidService: GuidService,
        private store: Store<AppState>,
        private authService: AuthenticationService,
        private lightCardsStoreService: LightCardsStoreService,
        private filterService: FilterService,
        private soundNotificationService: SoundNotificationService,
        private logger: OpfabLoggerService
    ) {
        const clientId = this.guidService.getCurrentGuidString();
        this.cardOperationsUrl = `${environment.urls.cards}/cardSubscription?clientId=${clientId}&version=${packageInfo.opfabVersion}`;
        this.deleteCardSubscriptionUrl = `${environment.urls.cards}/cardSubscription?clientId=${clientId}`;
        this.cardsUrl = `${environment.urls.cards}/cards`;
        this.archivesUrl = `${environment.urls.cards}/archives`;
        this.cardsPubUrl = `${environment.urls.cardspub}/cards`;
        this.userCardReadUrl = `${environment.urls.cardspub}/cards/userCardRead`;
        this.userCardUrl = `${environment.urls.cardspub}/cards/userCard`;
        this.checkHeartBeatReceive();
    }

    loadCard(id: string): Observable<CardData> {
        return this.httpClient.get<CardData>(`${this.cardsUrl}/${id}`).pipe(
            map((cardData) => {
                cardData.card.hasBeenAcknowledged =
                    this.lightCardsStoreService.isLightCardHasBeenAcknowledgedByUserOrByUserEntity(
                        fromCardToLightCard(cardData.card)
                    );
                return cardData;
            })
        );
    }

    public setSelectedCard(cardId) {
        this.selectedCardId = cardId;
    }

    async removeAndAddToTimeline(operation: any) {
        try {
            await this.removeCardFromTimeline(operation.card.id);
            this.addToTimeline(operation.card);
        } catch (error) {
            console.log("Timeline", "Une erreur est survenue :", error);
        }
    }
    
    removeCardFromTimeline(cardId: string): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            const cardElement = document.querySelector(`[event_id="${cardId}"]`);
    
            if (cardElement) {
                try {
                    cardElement.parentElement?.remove();
    
                    // Ajout d'un délai pour s'assurer que l'élément a été supprimé avant de résoudre la promesse
                    setTimeout(() => {
                        ["", "_end"].forEach(suffix => {
                            const iconElement = document.getElementById(`event${cardId}icon${suffix}`);
                            if (iconElement) {
                                iconElement.remove();
                            }
                        });
                        resolve();
                    }, 0);
                } catch (error) {
                    reject(error);
                }
            } else {
                console.log(`Timeline : La carte avec ID "${cardId}" n'existe pas.`);
                resolve();
            }
        });
    }
    
    public initCardSubscription() {
       
        var cards;
        this.getCardSubscription()
            .pipe(takeUntil(this.unsubscribe$))
            .subscribe({
                next: (operation) => {
                    switch (operation.type) {
                        case CardOperationType.ADD:
                            setTimeout(() => {
                                // document.getElementById("eventsForTimeLine").innerHTML = "";
                            }, 2000);
                            cards = $(".card");
                            setTimeout(() => {
                                $("#updateSeverity").click()
                                if (document.getElementById('usecase_hidden').innerText === "CAB DA" && document.getElementById("noevent_da").hidden){ 
                                    document.getElementById("noevent_da").hidden = true;
                                    document.getElementById("noevent_da_second").hidden = true;
                                    document.getElementById("da-fake-card").hidden = false;
                                    document.getElementById("fake-card-content-da").innerHTML = document.querySelector(".opfab-feed-list-card-severity").textContent + "<img id='opfab-card-icon' src='assets\/images\/info.svg' style='margin-left: 3px; float: right;'>";
                                    $("#setPolylineColor").click();
                                }
                            }, 4000);
                            // Pour démo DA 
                            setTimeout(() => {
                                if (document.getElementById('usecase_hidden').innerText === "CAB DA" && document.getElementById("noevent_da").hidden){ 
                                    $("#setPolylineColor").click();
                                    document.getElementById("fake-card-content-da").innerHTML = document.querySelector(".opfab-feed-list-card-severity").textContent + "<img id='opfab-card-icon' src='assets\/images\/info.svg' style='margin-left: 3px; float: right;'>";
                                }
                            }, 7000);
                            setTimeout(() => {
                                $("#updateHighlights").click()
                            }, 10000);
                            this.logger.info(
                                'CardService - Receive card to add id=' +
                                    operation.card.id +
                                    ' with date=' +
                                    new Date(operation.card.publishDate).toISOString(),
                                LogOption.LOCAL_AND_REMOTE
                            );
                            if(!operation.card.hasBeenAcknowledged){
                                this.removeAndAddToTimeline(operation);
                            }
                            this.lightCardsStoreService.addOrUpdateLightCard(operation.card);
                            if(operation.card.entityRecipients.includes('ORANGE')){
                                // TODO: color based on title and not metadata :(
                                setStatus(+/App_(\d+).*/.exec(operation.card.titleTranslated)[1], operation.card.severity)
                            }

                            if (operation.card.id === this.selectedCardId)
                                this.store.dispatch(new LoadCardAction({id: operation.card.id}));
                            break;
                        case CardOperationType.DELETE:
                            this.logger.info(
                                `CardService - Receive card to delete id=` + operation.cardId,
                                LogOption.LOCAL_AND_REMOTE
                            );
                            this.lightCardsStoreService.removeLightCard(operation.cardId);
                            if (operation.cardId === this.selectedCardId)
                                this.store.dispatch(new RemoveLightCardAction({card: operation.cardId}));
                            break;
                        case CardOperationType.ACK:
                            this.logger.info(
                                'CardService - Receive ack on card uid=' +
                                    operation.cardUid +
                                    ', id=' +
                                    operation.cardId,
                                LogOption.LOCAL_AND_REMOTE
                            );
                            this.lightCardsStoreService.addEntitiesAcksForLightCard(
                                operation.cardId,
                                operation.entitiesAcks
                            );
                            this.receivedAcksSubject.next({
                                cardUid: operation.cardUid,
                                entitiesAcks: operation.entitiesAcks
                            });
                            break;
                        default:
                            this.logger.info(
                                `CardService - Unknown operation ` +
                                    operation.type +
                                    ` for card id=` +
                                    operation.cardId,
                                LogOption.LOCAL_AND_REMOTE
                            );
                    }
                },
                error: (error) => {
                    console.error('CardService - Error received from  getCardSubscription ', error);
                }
            });
        catchError((error, caught) => {
            console.error('CardService - Global  error in subscription ', error);
            return caught;
        });
        this.listenForFilterChange();
    }

    private listenForFilterChange() {
        this.filterService.getBusinessDateFilterChanges().subscribe((filter) => {
            this.setSubscriptionDates(filter.status.start, filter.status.end);
        });
    }

    public closeSubscription() {
        if (!this.subscriptionClosed) {
            this.logger.info('Closing subscription', LogOption.LOCAL_AND_REMOTE);
            this.deleteCardSubscription().subscribe();
            this.unsubscribe$.next();
            this.unsubscribe$.complete();
            this.subscriptionClosed = true;
        }
    }

    public addToTimeline(card){
                    var criticality = card.severity;
                    var criticalities ;
                    var use_case = card.entityRecipients[0];
                    var date = card.startDate;
                    var end_date = card.endDate;
                    var title = card.title.parameters.title;
                    var description = card.description;
                    var id_event = card.id;
                    var uid = card.uid;
                    var heure_event = this.time_format(new Date(date));
                    var heure_event_fin = end_date ? this.time_format(new Date(end_date)) : null;
                    var id_bloc_event = document.getElementById("event" + card)
                    fetch('./shared/json_samples/criticalities.json')
                    .then(response => response.json())
                    .then(data => {
                      criticalities = data.criticalities;
                      var cardToAdd = "<div class='blocEvent' id='event" + id_event  + "'>" +
                            "<div class='bloc_title'" + "style = 'width: 185px;position:absolute;z-index: 2;height: 40px;background-color:var(--opfab-bgcolor);color:"+ criticalities[use_case].color[criticality] + 
                            ";border: 1px solid " + criticalities[use_case].color[criticality] + ';box-shadow: -4px 0px 0px ' + criticalities[use_case].color[criticality] + "' event_id='"+ id_event + "'" +
                            " id='title" + id_event + "'>" + "<div>"+title +"</div>" + "<div style='position:absolute;right:0px;'>"+criticalities[use_case].icon.timeline[criticality] + "</div>" + "</div>" + "<div class='timeline'>" +
                            "<div class='timeline-line'><d<div class='timeline-hour' style='left: 0;'></div><div class='timeline-hour' style='left: 25%;'></div>" +
                            "<div class='timeline-hour' style='left: 50%;'></div><div class='timeline-hour' style='left: 75%;'></div><div class='timeline-hour' style='right: 0;'></div></div>" +
                            "<div class='timeline-point tl-point' id='timeline-point" + id_event + "'>" 
                            + "<span class='tl_hour' start_date='" + heure_event + "'>" + heure_event + "</span>" 
                            + criticalities[use_case].icon[criticality] + "</div>" +
                            "<div class='timeline-point-end tl-point' id='timeline-point-end" + id_event + "'>" + (heure_event_fin !== null ? "<span class='tl_hour'>" + heure_event_fin + "</span><img src='assets/images/done.png'>" : "") + "</div>" +
                            "<div class='timeline-highlight' id='timeline-highlight" + id_event + "' style='position:absolute;color: " + criticalities[use_case].color[criticality] + "' hidden></div></div>";
                            document.getElementById("eventsForTimeLine").innerHTML += cardToAdd;

                        })
                    .catch(error => {
                      console.error('Erreur lors de la lecture du fichier JSON :', error);
                    });
                 
                    setTimeout(() => {
                        
                        this.waitForElementCreation(`timeline-point${id_event}`)
                        .then(() => this.positionnerPointSurTimeline(heure_event, id_event, heure_event_fin))
                        .then(() => this.waitForElementCreation(`event${id_event}icon`))
                        .then(() => this.getCardForTimeline(id_event, uid, use_case))

                        setTimeout(() => {
                            if(heure_event_fin){

                            }
                        }, 2000);
                      

                        
                    }, 2000);
    }

    private waitForElementCreation(elementId: string): Promise<void> {
        return new Promise<void>((resolve) => {
            const checkElement = () => {
                const element = document.getElementById(elementId);
                if (element) {
                    resolve();
                } else {
                    setTimeout(checkElement, 100); 
                }
            };
    
            checkElement(); 
        });
    }
    public getCardForTimeline(id_event, uid, use_case) {
        if (document.querySelector(`[data-urlid="${id_event}"]`).querySelector(".imgBin") == null) {
            var trashIconSrc = use_case !== "DA" ? "assets/images/trashIcon.svg" : "assets/images/trashIconDA.svg";
            document.querySelector(`[data-urlid="${id_event}"]`).innerHTML += '<img class="imgBin" src="' + trashIconSrc + '" width="10%" onclick="event.stopPropagation();acknowledgeEvent(\'' + uid + '\', \'' + id_event + '\', \'' + id_event + '\')">';
        }
    }
    
    public positionnerPointSurTimeline(heure, timeline_id,end_date) {

        var point = document.getElementById('timeline-point' + timeline_id);
        var highlight = document.getElementById('timeline-highlight' + timeline_id);
        var heureRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
        if (!heureRegex.test(heure)) {
            console.error("Format d'heure invalide. Utilisez le format HH:mm.");
            return;
        }
        var end_date;
        var heureMinutes = heure.split(':');
        var heures = parseInt(heureMinutes[0]);
        var minutes = parseInt(heureMinutes[1]);
        var heureEvent = new Date();
        heureEvent.setHours(heures, minutes, 0, 0);
        highlight.hidden = false;
        setTimeout(() => {
            var originIcon = (document.getElementById("title" + timeline_id).parentElement.querySelector(".timeline-point img") as HTMLImageElement | null)?.src || '';
            var originLeft = (document.getElementById("title" + timeline_id).parentElement.querySelector(".timeline-point") as HTMLImageElement | null)?.style.left || '';
    
            document.getElementById("timeline-line").innerHTML += "<img id='event" + timeline_id + "icon'" + "src='" + originIcon + "'" + ">";
            document.getElementById("event" + timeline_id + "icon").style.left = originLeft;
            document.getElementById("event" + timeline_id + "icon").style.marginLeft = "-5px";
            document.getElementById("event" + timeline_id + "icon").style.position = "absolute"
            document.getElementById("event" + timeline_id + "icon").style.marginTop = "-27px"
            if(end_date){
                    this.positionnerPointFinDateEventSurTimeline(end_date,timeline_id)
                    var end_timelineHighlightWidth = document.getElementById("timeline-point"+timeline_id).getBoundingClientRect().left - document.getElementById("timeline-point-end"+timeline_id).getBoundingClientRect().left;
                    highlight.style.width = Math.abs(end_timelineHighlightWidth) + "px";
                    highlight.style.left = "calc(" + positionEnPourcentage + "% - 4px)";
                    var originIconEnd = (document.getElementById("title" + timeline_id).parentElement.querySelector(".timeline-point-end img") as HTMLImageElement | null)?.src || '';
                    var originLeftEnd = (document.getElementById("title" + timeline_id).parentElement.querySelector(".timeline-point-end") as HTMLImageElement | null)?.style.left || '';
                    document.getElementById("timeline-line").innerHTML += "<img id='event" + timeline_id + "icon_end'" + "src='" + originIconEnd + "'" + ">";
                    document.getElementById("event" + timeline_id + "icon_end").style.left = originLeftEnd
                    document.getElementById("event" + timeline_id + "icon_end").style.position = "absolute"
                    document.getElementById("event" + timeline_id + "icon_end").style.marginTop = "-27px"



            }else{
                    if (new Date() > new Date(new Date().setHours(heures, minutes))) { 
                    var timelineHighlightWidth = document.getElementById("timeline-point"+timeline_id).getBoundingClientRect().left - document.getElementsByClassName("global-current-time-cursor")[0].getBoundingClientRect().left;
                    highlight.style.width = Math.abs(timelineHighlightWidth) + "px";
                    highlight.style.left = "calc(" + positionEnPourcentage + "% - 4px)";
                }
                

            }
        }, 5000);

        if (heures < 0 || heures > 23 || minutes < 0 || minutes > 59) {
            console.error("Heure invalide. Assurez-vous que l'heure est entre 00:00 et 23:59.");
            return;
        }
            var positionEnPourcentage = ((heures * 60 + minutes) / 1440) * 100;
            point.style.left = "calc(" + positionEnPourcentage + "%)";
        }


    private deleteCardSubscription(): Observable<HttpResponse<void>> {
        return this.httpClient.delete<any>(`${this.deleteCardSubscriptionUrl}`, {observe: 'response'});
    }

    public positionnerPointFinDateEventSurTimeline(heure, timeline_id) {

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
    }
    private getCardSubscription(): Observable<CardOperation> {
        // security header needed here as SSE request are not intercepted by our header interceptor
        let securityHeader;
        if (!this.authService.isAuthModeNone()) {
            securityHeader = this.authService.getSecurityHeader();
        }
        const eventSource = new EventSourcePolyfill(`${this.cardOperationsUrl}&notification=true`, {
            headers: securityHeader
            // if necessary, we can set here heartbeatTimeout: xxx (in ms)
        });
        return new Observable((observer) => {
            try {
                eventSource.onmessage = (message) => {
                    if (!message) {
                        return observer.error(message);
                    }
                    switch (message.data) {
                        case 'RELOAD':
                            this.logger.info(`CardService - RELOAD received`, LogOption.LOCAL_AND_REMOTE);
                            this.store.dispatch(new UIReloadRequestedAction());
                            break;
                        case 'INIT':
                            console.log(new Date().toISOString(), `CardService - Card subscription initialized`);
                            this.initSubscription.next();
                            this.initSubscription.complete();
                            if (this.firstSubscriptionInitDone) {
                                this.recoverAnyLostCardWhenConnectionHasBeenReset();
                                // process or user config may have change during connection loss
                                // so reload both configuration
                                this.store.dispatch(new BusinessConfigChangeAction());
                                this.store.dispatch(new UserConfigChangeAction());
                            } else {
                                this.firstSubscriptionInitDone = true;
                                this.lastHeardBeatDate = new Date().valueOf();
                            }
                            break;
                        case 'HEARTBEAT':
                            this.lastHeardBeatDate = new Date().valueOf();
                            this.logger.info(`CardService - HEARTBEAT received - Connection alive `, LogOption.LOCAL);
                            break;
                        case 'BUSINESS_CONFIG_CHANGE':
                            this.store.dispatch(new BusinessConfigChangeAction());
                            this.logger.info(`CardService - BUSINESS_CONFIG_CHANGE received`);
                            break;
                        case 'USER_CONFIG_CHANGE':
                            this.store.dispatch(new UserConfigChangeAction());
                            this.logger.info(`CardService - USER_CONFIG_CHANGE received`);
                            break;
                        case 'DISCONNECT_USER_DUE_TO_NEW_CONNECTION':
                            this.logger.info(
                                'CardService - Disconnecting user because a new connection is being opened for this account'
                            );
                            this.soundNotificationService.stopService();
                            this.closeSubscription();
                            this.receivedDisconnectedSubject.next(true);
                            break;
                        default:
                            return observer.next(JSON.parse(message.data, CardOperation.convertTypeIntoEnum));
                    }
                };
                eventSource.onerror = (error) => {
                    this.store.dispatch(new CardSubscriptionClosedAction());
                    console.error(new Date().toISOString(), 'CardService - Error event in card subscription:', error);
                };
                eventSource.onopen = (open) => {
                    this.store.dispatch(new CardSubscriptionOpenAction());
                    console.log(new Date().toISOString(), `CardService- Open card subscription`);
                };
            } catch (error) {
                console.error(
                    new Date().toISOString(),
                    'CardService - Error in interpreting message from subscription',
                    error
                );
                return observer.error(error);
            }
            return () => {
                if (eventSource && eventSource.readyState !== eventSource.CLOSED) {
                    eventSource.close();
                }
            };
        });
    }

    private checkHeartBeatReceive() {
        setInterval(() => {
            this.logger.info(
                'Last heart beat received ' + (new Date().valueOf() - this.lastHeardBeatDate) + 'ms ago',
                LogOption.LOCAL_AND_REMOTE
            );
        }, 60000);
    }

    private recoverAnyLostCardWhenConnectionHasBeenReset() {
        // Subtracts two minutes from the last heart beat to avoid loosing card due to latency, buffering and not synchronized clock
        const dateForRecovering = this.lastHeardBeatDate - CardService.TWO_MINUTES;
        this.logger.info(
            `CardService - Card subscription has been init again , recover any lost card from date ` +
                new Date(dateForRecovering),
            LogOption.LOCAL_AND_REMOTE
        );
        this.httpClient.post<any>(`${this.cardOperationsUrl}`, {publishFrom: dateForRecovering}).subscribe();
    }

    public time_format(d) {
        var hours = this.format_two_digits(d.getHours());
        var minutes = this.format_two_digits(d.getMinutes());
        return hours + ":" + minutes;
    }

    public format_two_digits(n) {
        return n < 10 ? '0' + n : n;
    }
    public removeAllLightCardFromMemory() {
        this.startOfAlreadyLoadedPeriod = null;
        this.lightCardsStoreService.removeAllLightCards();
    }

    private setSubscriptionDates(start: number, end: number) {
        this.logger.info(
            'CardService - Set subscription date' + new Date(start) + ' -' + new Date(end),
            LogOption.LOCAL_AND_REMOTE
        );
        if (!this.startOfAlreadyLoadedPeriod) {
            // First loading , no card loaded yet
            this.askCardsForPeriod(start, end);
            return;
        }
        if (start < this.startOfAlreadyLoadedPeriod && end > this.endOfAlreadyLoadedPeriod) {
            this.askCardsForPeriod(start, end);
            return;
        }
        if (start < this.startOfAlreadyLoadedPeriod) {
            this.askCardsForPeriod(start, this.startOfAlreadyLoadedPeriod);
            return;
        }
        if (end > this.endOfAlreadyLoadedPeriod) {
            this.askCardsForPeriod(this.endOfAlreadyLoadedPeriod, end);
            return;
        }
        this.logger.info('CardService - Card already loaded for the chosen period', LogOption.LOCAL_AND_REMOTE);
    }

    private askCardsForPeriod(start: number, end: number) {
        this.logger.info(
            'CardService - Need to load card for period ' + new Date(start) + ' -' + new Date(end),
            LogOption.LOCAL_AND_REMOTE
        );
        this.httpClient
            .post<any>(`${this.cardOperationsUrl}`, {rangeStart: start, rangeEnd: end})
            .subscribe((result) => {
                if (!this.startOfAlreadyLoadedPeriod || start < this.startOfAlreadyLoadedPeriod)
                    this.startOfAlreadyLoadedPeriod = start;
                if (!this.endOfAlreadyLoadedPeriod || end > this.endOfAlreadyLoadedPeriod)
                    this.endOfAlreadyLoadedPeriod = end;
            });
    }

    loadArchivedCard(id: string): Observable<CardData> {
        return this.httpClient.get<CardData>(`${this.archivesUrl}/${id}`);
    }

    fetchArchivedCards(filters: Map<string, string[]>): Observable<Page<LightCard>> {
        const params = this.convertFiltersIntoHttpParams(filters);
        return this.httpClient.get<Page<LightCard>>(`${this.archivesUrl}/`, {params});
    }

    convertFiltersIntoHttpParams(filters: Map<string, string[]>): HttpParams {
        let params = new HttpParams();
        filters.forEach((values, key) => values.forEach((value) => (params = params.append(key, value))));
        return params;
    }

    postCard(card: CardForPublishing): any {
        return this.httpClient.post<CardForPublishing>(`${this.cardsPubUrl}/userCard`, card, {observe: 'response'});
    }

    deleteCard(card: Card): Observable<HttpResponse<void>> {
        return this.httpClient.delete<void>(`${this.userCardUrl}/${card.id}`, {observe: 'response'});
    }

    postUserCardRead(cardUid: string): Observable<HttpResponse<void>> {
        return this.httpClient.post<void>(`${this.userCardReadUrl}/${cardUid}`, null, {observe: 'response'});
    }

    deleteUserCardRead(cardUid: string): Observable<HttpResponse<void>> {
        return this.httpClient.delete<void>(`${this.userCardReadUrl}/${cardUid}`, {observe: 'response'});
    }

    postTranslateCardField(processId: string, processVersion: string, i18nValue: I18n): any {
        const fieldToTranslate = {process: processId, processVersion: processVersion, i18nValue: i18nValue};
        return this.httpClient.post<any>(`${this.cardsPubUrl}/translateCardField`, fieldToTranslate, {
            observe: 'response'
        });
    }

    getReceivedAcks(): Observable<{cardUid: string; entitiesAcks: string[]}> {
        return this.receivedAcksSubject.asObservable();
    }

    getReceivedDisconnectUser(): Observable<boolean> {
        return this.receivedDisconnectedSubject.asObservable();
    }
}
