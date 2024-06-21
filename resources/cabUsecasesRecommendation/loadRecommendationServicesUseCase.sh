cd "$(dirname "${BASH_SOURCE[0]}")"

 ./createEventUsecase.sh daRecommendationUC $1
 ./createEventUsecase.sh orangeRecommendationUC $1
 ./createEventUsecase.sh rteRecommendationUC $1
 ./createEventUsecase.sh sncfRecommendationUC $1