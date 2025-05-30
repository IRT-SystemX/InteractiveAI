#!/bin/bash

# Copyright (c) 2021, RTE (http://www.rte-france.com)
# See AUTHORS.txt
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
# This file is part of the OperatorFabric project.


url=$1
if [ -z $url ] 
then
	url="http://localhost"
fi

source ./getToken.sh "admin" $url:3200/auth/token
curl $url:3200/cards/connections -H "Authorization:Bearer $token"
echo ""