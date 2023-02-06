#!/bin/bash

# Copyright (c) 2021-2022, RTE (http://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of the OperatorFabric project.

# This starts by moving to the directory where the script is located so the paths below still work even if the script
# is called from another folder
cd "$(dirname "${BASH_SOURCE[0]}")"

for d in *.json; do
    perimeter=${d:0:$((${#d} - 5))} #remove last 5 character
    ./createPerimeter.sh  $perimeter $1
done

 ./addPerimeterToGroup.sh rteProcess Dispatcher $1
 ./addPerimeterToGroup.sh rteProcess Planner $1
 ./addPerimeterToGroup.sh rteProcess Supervisor $1
 ./addPerimeterToGroup.sh sncfProcess Dispatcher $1
 ./addPerimeterToGroup.sh sncfProcess Planner $1
 ./addPerimeterToGroup.sh sncfProcess Supervisor $1
 ./addPerimeterToGroup.sh daProcess Dispatcher $1
 ./addPerimeterToGroup.sh daProcess Planner $1
 ./addPerimeterToGroup.sh daProcess Supervisor $1
 ./addPerimeterToGroup.sh orangeProcess Dispatcher $1
 ./addPerimeterToGroup.sh orangeProcess Planner $1
 ./addPerimeterToGroup.sh orangeProcess Supervisor $1
 