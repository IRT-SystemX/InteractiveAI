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
        auth: 'localhost:3200/auth',
        cards: 'localhost:3200/cards',
        cardspub: 'localhost:3200/cardspub',
        users: 'localhost:3200/users',
        groups: 'localhost:3200/users/groups',
        entities: 'localhost:3200/users/entities',
        perimeters: 'localhost:3200/users/perimeters',
        archives: '',
        processes: 'localhost:3200/businessconfig/processes',
        processGroups: 'localhost:3200/businessconfig/processgroups',
        realTimeScreens: 'localhost:3200/businessconfig/realtimescreens',
        monitoringConfig: 'localhost:3200/businessconfig/monitoring',
        config: 'localhost:3200/config/web-ui.json',
        menuConfig: 'localhost:3200/config/ui-menu.json',
        externalDevices: 'localhost:3200/externaldevices',
        remoteLogs: 'localhost:3200/cards/logs'
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