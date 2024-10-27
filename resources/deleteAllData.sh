#!/bin/bash

./deleteServiceData.sh cabcontext localhost
./deleteServiceData.sh cab_event localhost
./deleteServiceData.sh cabhistoric localhost
./deleteAllArchivedCards.sh
./deleteAllCards.sh
./deleteAllSettings.sh