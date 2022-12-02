/* Copyright (c) 2022, RTE (http://www.rte-france.com)
 * See AUTHORS.txt
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 * SPDX-License-Identifier: MPL-2.0
 * This file is part of the OperatorFabric project.
 */


const opfabStyle = {

    rootRulesNumber : null,
    rootStyleSheet : null,

    init: function() {
        this.rootStyleSheet = document.styleSheets[0];
        const len = document.styleSheets.length;
        for (let n = 0; n < len; n++) {
            if (document.styleSheets[n].title === 'opfabRootStyle') {
                this.rootStyleSheet = document.styleSheets[n];
                break;
            }
        }
    },

    setCss:  function(cssRule) {
        if (this.rootRulesNumber) {
            this.rootStyleSheet.deleteRule(this.rootRulesNumber);
        }
        this.rootRulesNumber = this.rootStyleSheet.insertRule(
            cssRule,
            this.rootStyleSheet.cssRules.length
        );
    },


    DAY_STYLE : `:root { --opfab-bgcolor: white;
        --opfab-bgcolor-darker: #F3F2F1;
        --opfab-font-family: 'Open Sans', sans-serif;
        --opfab-text-color: black;
        --opfab-text-color-stronger: black;
        --opfab-table-border-color: grey;
        --opfab-input-text-color : black;
        --opfab-form-label-text-color: black;
        --opfab-form-border-color:  #9C9B9B;
        --opfab-button-disable-bgcolor: #DBDBDB;
        --opfab-popover-bgcolor: #f3f2f1;
        --opfab-feedbar-icon-color: black;
        --opfab-feedbar-icon-hover-color:#212529;
        --opfab-feedbar-icon-hover-bgcolor: #F3F2F1;
        --opfab-timeline-bgcolor: #white;
        --opfab-timeline-text-color: #000000;
        --opfab-timeline-grid-color: #C9CCD1;
        --opfab-timeline-week-color: #aaaaaa;
        --opfab-timeline-week-color2: #aaaaaa;
        --opfab-timeline-week-bgcolor: #ffffff;
        --opfab-timeline-realtimebar-color: #2784FF;
        --opfab-timeline-button-bgcolor: #e5e5e5;
        --opfab-timeline-button-text-color: #49494a;
        --opfab-timeline-button-selected-bgcolor: #49494a;
        --opfab-timeline-button-selected-text-color: #fcfdfd;
        --opfab-lightcard-detail-bgcolor: #F3F2F1;
        --opfab-lightcard-detail-textcolor: black;
        --opfab-lightcard-detail-border-color: #cccccc;
        --opfab-lightcard-detail-selected-bgcolor: #E1E1E1;
        --opfab-lightcard-detail-unread-textcolor: black;
        --opfab-light-card-lttd-timeleft: #ff6600;
        --opfab-card-tab-selected-text-color: black;
        --opfab-card-tab-border-color: ##111D2D;
        --opfab-card-bgcolor : #F3F2F1;
        --opfab-card-shadow: 0 2px 4px 0 rgba(0,0,0,0.5);
        --opfab-card-detail-border-color : #dddddd;
        --opfab-navbar-color: black;
        --opfab-navbar-color-hover:black;
        --opfab-navbar-color-active:#0d6efd;
        --opfab-navbar-toggler-icon: url("data:image/svg+xml, %3csvg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 30 30'%3e%3cpath stroke='rgba(0,0,0, 0.55)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
        --opfab-navbar-toggler-border-color: rgba(0,0,0,.1) ;
        --opfab-navbar-info-block-color: rgba(0,0,0,.9);
        --opfab-navbar-menu-link-color: #343a40;
        --opfab-navbar-menu-link-hover-color: #121416;
        --opfab-navbar-menu-bgcolor: white;
        --opfab-navbar-right-menu-bgcolor: #f3f2f1;
        --opfab-navbar-menu-bgcolor-item-active: #007bff;
        --opfab-navbar-menu-bgcolor-item-hover: #f8f9fa;
        --opfab-timeline-cardlink: #212529;
        --opfab-timeline-cardlink-bgcolor-hover: #e2e6ea;
        --opfab-timeline-cardlink-bordercolor-hover: #dae0e5;
        --opfab-calendar-grid-color : #C9CCD1;
        --opfab-scrollbar-bgcolor: #ffffff;
        --opfab-scrollbar-border-color: #979797;
        --opfab-scrollbar-bar-bgcolor: #BFC1C7;
        --opfab-scrollbar-bar-border-color: #979797;
        --opfab-scrollbar-bgcolor-firefox: #dddddd;
        --opfab-scrollbar-bar-bgcolor-firefox: #bbbbbb;
        --opfab-pagination-active-page-background: #909090;
        --opfab-pagination-disabled-link: #808080;
        }`,

    NIGHT_STYLE : `:root { --opfab-bgcolor: white;
        --opfab-bgcolor-darker: #F3F2F1;
        --opfab-font-family: 'Open Sans', sans-serif;
        --opfab-text-color: black;
        --opfab-text-color-stronger: black;
        --opfab-table-border-color: grey;
        --opfab-input-text-color : black;
        --opfab-form-label-text-color: black;
        --opfab-form-border-color:  #9C9B9B;
        --opfab-button-disable-bgcolor: #DBDBDB;
        --opfab-popover-bgcolor: #f3f2f1;
        --opfab-feedbar-icon-color: black;
        --opfab-feedbar-icon-hover-color:#212529;
        --opfab-feedbar-icon-hover-bgcolor: #F3F2F1;
        --opfab-timeline-bgcolor: #white;
        --opfab-timeline-text-color: #000000;
        --opfab-timeline-grid-color: #C9CCD1;
        --opfab-timeline-week-color: #aaaaaa;
        --opfab-timeline-week-color2: #aaaaaa;
        --opfab-timeline-week-bgcolor: #ffffff;
        --opfab-timeline-realtimebar-color: #2784FF;
        --opfab-timeline-button-bgcolor: #e5e5e5;
        --opfab-timeline-button-text-color: #49494a;
        --opfab-timeline-button-selected-bgcolor: #49494a;
        --opfab-timeline-button-selected-text-color: #fcfdfd;
        --opfab-lightcard-detail-bgcolor: #F3F2F1;
        --opfab-lightcard-detail-textcolor: black;
        --opfab-lightcard-detail-border-color: #cccccc;
        --opfab-lightcard-detail-selected-bgcolor: #E1E1E1;
        --opfab-lightcard-detail-unread-textcolor: black;
        --opfab-light-card-lttd-timeleft: #ff6600;
        --opfab-card-tab-selected-text-color: black;
        --opfab-card-tab-border-color: ##111D2D;
        --opfab-card-bgcolor : #F3F2F1;
        --opfab-card-shadow: 0 2px 4px 0 rgba(0,0,0,0.5);
        --opfab-card-detail-border-color : #dddddd;
        --opfab-navbar-color: black;
        --opfab-navbar-color-hover:black;
        --opfab-navbar-color-active:#0d6efd;
        --opfab-navbar-toggler-icon: url("data:image/svg+xml, %3csvg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 30 30'%3e%3cpath stroke='rgba(0,0,0, 0.55)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
        --opfab-navbar-toggler-border-color: rgba(0,0,0,.1) ;
        --opfab-navbar-info-block-color: rgba(0,0,0,.9);
        --opfab-navbar-menu-link-color: #343a40;
        --opfab-navbar-menu-link-hover-color: #121416;
        --opfab-navbar-menu-bgcolor: white;
        --opfab-navbar-right-menu-bgcolor: #f3f2f1;
        --opfab-navbar-menu-bgcolor-item-active: #007bff;
        --opfab-navbar-menu-bgcolor-item-hover: #f8f9fa;
        --opfab-timeline-cardlink: #212529;
        --opfab-timeline-cardlink-bgcolor-hover: #e2e6ea;
        --opfab-timeline-cardlink-bordercolor-hover: #dae0e5;
        --opfab-calendar-grid-color : #C9CCD1;
        --opfab-scrollbar-bgcolor: #ffffff;
        --opfab-scrollbar-border-color: #979797;
        --opfab-scrollbar-bar-bgcolor: #BFC1C7;
        --opfab-scrollbar-bar-border-color: #979797;
        --opfab-scrollbar-bgcolor-firefox: #dddddd;
        --opfab-scrollbar-bar-bgcolor-firefox: #bbbbbb;
        --opfab-pagination-active-page-background: #909090;
        --opfab-pagination-disabled-link: #808080;
        }`

    
}



