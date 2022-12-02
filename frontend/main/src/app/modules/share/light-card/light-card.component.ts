/* Copyright (c) 2018-2022, RTE (http://www.rte-france.com)
 * See AUTHORS.txt
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 * SPDX-License-Identifier: MPL-2.0
 * This file is part of the OperatorFabric project.
 */

import {Component, Input, OnDestroy, OnInit} from '@angular/core';
import {LightCard} from '@ofModel/light-card.model';
import {Router} from '@angular/router';
import {selectCurrentUrl} from '@ofStore/selectors/router.selectors';
import {Store} from '@ngrx/store';
import {AppState} from '@ofStore/index';
import {takeUntil} from 'rxjs/operators';
import {Observable, Subject} from 'rxjs';
import {ConfigService} from '@ofServices/config.service';
import {AppService, PageType} from '@ofServices/app.service';
import {EntitiesService} from '@ofServices/entities.service';
import {ProcessesService} from '@ofServices/processes.service';
import {UserPreferencesService} from '@ofServices/user-preference.service';
import {DisplayContext} from '@ofModel/templateGateway.model';
import {GroupedCardsService} from '@ofServices/grouped-cards.service';
import {TypeOfStateEnum} from '@ofModel/processes.model';
import {SoundNotificationService} from '@ofServices/sound-notification.service';
import {DateTimeFormatterService} from '@ofServices/date-time-formatter.service';
import {MapService} from '@ofServices/map.service';
import $, { get } from "jquery";

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
    ) {}

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
    public getCardTitle(){
            if (document.getElementById("opfab-card-title").innerHTML.includes("Surcharge") && !document.getElementById("opfab-card-title").innerHTML.includes("54_58_154")){
                $("#opfab-div-card-template-security").hide()
                $("#opfab-div-card-template-op").hide()
                $("#opfab-div-card-template-alarm").show()
                $("#opfab-div-card-template").hide()
                $("#opfab-div-card-template-noparades").hide()
                $("#opfab-div-card-template-agent").hide()
                $.get( "http://192.168.208.57:5100/api/v1/contexts?time="+new Date().getTime(), function( data ) {
                   $("#ctxImg").attr("src","data:image/png;base64,"+data[0].data.topology)
                   $(".opfab-card-response-header").hide();
                  });
            }else if(document.getElementById("opfab-card-title").innerHTML.includes("Risque sur aléa")){
                $("#opfab-div-card-template-security").show()
                $("#opfab-div-card-template-op").hide()
                $("#opfab-div-card-template-alarm").hide()
                $("#opfab-div-card-template-noparades").hide()
                $("#opfab-div-card-template-agent").hide()
                }
            else if(document.getElementById("opfab-card-title").innerHTML.includes("Alerte Agent")){
                $("#opfab-div-card-template-agent").show()
                $("#opfab-div-card-template-security").hide()
                $("#opfab-div-card-template-op").hide()
                $("#opfab-div-card-template-alarm").hide()
                $("#opfab-div-card-template-noparades").hide()
            }else if (document.getElementById("opfab-card-title").innerHTML.includes("Surcharge") 
            && document.getElementById("opfab-card-title").innerHTML.includes("54_58_154")){
                $("#opfab-div-card-template-security").hide()
                $("#opfab-div-card-template-op").hide()
                $("#opfab-div-card-template-alarm").hide()
                $("#opfab-div-card-template").hide()
                $("#opfab-div-card-template-noparades").show()
                $("#opfab-div-card-template-agent").hide()
                $.get( "http://192.168.208.57:5100/api/v1/contexts?time="+new Date().getTime(), function( data ) {
                   $("#ctxImg").attr("src","data:image/png;base64,"+data[0].data.topology)
                   $(".opfab-card-response-header").hide();
                  });
            }else if(document.getElementById("opfab-card-title").innerHTML.includes("Retour de ligne")  || document.getElementById("opfab-card-title").innerHTML.includes("Retrait de ligne")) {
                        $("#opfab-div-card-template").hide()
                        $("#opfab-div-card-template-op").show()
                        $("#opfab-div-card-template-security").hide()
                        $("#opfab-div-card-template-alarm").hide()
                        $("#opfab-div-card-template-noparades").hide()
            }

    }
    public select($event) {
        var card = $event.path[2].firstChild.offsetParent.outerText;
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
                this.getCardTitle()
            }, 1000);
            // if(card.includes("Surcharge")){
            //     $("#opfab-div-card-template-security").hide()
            //     $("#opfab-div-card-template-op").hide()
            //     $("#opfab-div-card-template-alarm").show()
            //     $("#opfab-div-card-template").hide()
            //     $("#opfab-div-card-template-noparades").hide()

            //     $.get( "http://192.168.208.57:5100/api/v1/contexts?time="+new Date().getTime(), function( data ) {
            //        $("#ctxImg").attr("src","data:image/png;base64,"+data[0].data.topology)
            //        $(".opfab-card-response-header").hide();
            //       });
            //     }else if(card.includes("Routine")) {
            //         $("#opfab-div-card-template").hide()
            //         $("#opfab-div-card-template-op").show()
            //         $("#opfab-div-card-template-security").hide()
            //         $("#opfab-div-card-template-alarm").hide()
            //         $("#opfab-div-card-template-noparades").hide()
            //     }else if(card.includes("Risque sur aléa")){
            //         $("#opfab-div-card-template-security").show()
            //         $("#opfab-div-card-template-op").hide()
            //         $("#opfab-div-card-template-alarm").hide()
            //         $("#opfab-div-card-template-noparades").hide()
            //         }else if (card.includes("Surcharge de ligne") && card.includes("54_58_154")){
            //             $("#opfab-div-card-template-noparades").show()
            //             $("#opfab-div-card-template-security").hide()
            //             $("#opfab-div-card-template-op").hide()
            //             $("#opfab-div-card-template-alarm").hide()

            //         }
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
