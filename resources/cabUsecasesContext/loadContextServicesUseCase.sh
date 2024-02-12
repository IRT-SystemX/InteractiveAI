cd "$(dirname "${BASH_SOURCE[0]}")"

 ./createContextUsecase.sh daContext $1
 ./createContextUsecase.sh orangeContext $1
 ./createContextUsecase.sh rteContext $1
 ./createContextUsecase.sh sncfContext $1