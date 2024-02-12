cd "$(dirname "${BASH_SOURCE[0]}")"

 ./createEventUsecase.sh daEvent $1
 ./createEventUsecase.sh orangeEvent $1
 ./createEventUsecase.sh rteEvent $1
 ./createEventUsecase.sh sncfEvent $1