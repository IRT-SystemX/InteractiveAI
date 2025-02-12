cd "$(dirname "${BASH_SOURCE[0]}")"

 ./createEventUsecase.sh ATMEvent $1
 ./createEventUsecase.sh PowerGridEvent $1
 ./createEventUsecase.sh RailwayEvent $1