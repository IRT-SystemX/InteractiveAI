cd "$(dirname "${BASH_SOURCE[0]}")"

 ./createContextUsecase.sh PowerGridContext $1
 ./createContextUsecase.sh ATMContext $1
 ./createContextUsecase.sh RailwayContext $1
 