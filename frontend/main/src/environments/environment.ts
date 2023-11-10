/* Copyright (c) 2018-2022, RTE (http://www.rte-france.com)
 * See AUTHORS.txt
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 * SPDX-License-Identifier: MPL-2.0
 * This file is part of the OperatorFabric project.
 */

// This file can be replaced during build by using the `fileReplacements` array.
// `ng build ---prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
    production: false,
    urls: {
        authentication: '',
        auth: 'http://192.168.211.95:3200/auth',
        cards: 'http://192.168.211.95:3200/cards',
        cardspub: 'http://192.168.211.95:3200/cardspub',
        users: 'http://192.168.211.95:3200/users',
        groups: 'http://192.168.211.95:3200/users/groups',
        entities: 'http://192.168.211.95:3200/users/entities',
        perimeters: 'http://192.168.211.95:3200/users/perimeters',
        archives: '',
        processes: 'http://192.168.211.95:3200/businessconfig/processes',
        processGroups: 'http://192.168.211.95:3200/businessconfig/processgroups',
        realTimeScreens: 'http://192.168.211.95:3200/businessconfig/realtimescreens',
        monitoringConfig: 'http://192.168.211.95:3200/businessconfig/monitoring',
        config: 'http://192.168.211.95:3200/config/web-ui.json',
        menuConfig: 'http://192.168.211.95:3200/config/ui-menu.json',
        externalDevices: 'http://192.168.211.95:3200/externaldevices',
        remoteLogs: 'http://192.168.211.95:3200/cards/logs'
    },
    paths: {
        i18n: '/assets/i18n/'
    }
};

/*
 * In development mode, to ignore zone related message stack frames such as
 * `zone.run`, `zoneDelegate.invokeTask` for easier debugging, you can
 * import the following file, but please comment it out in production mode
 * because it will have performance impact when throw message
 */
// import 'zone.js/plugins/zone-message';  // Included with Angular CLI.