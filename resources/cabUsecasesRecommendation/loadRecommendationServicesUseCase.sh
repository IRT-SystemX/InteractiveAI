cd "$(dirname "${BASH_SOURCE[0]}")"

 ./createRecommendationUsecase.sh daRecommendationUC $1
 ./createRecommendationUsecase.sh rteRecommendationUC $1
 ./createRecommendationUsecase.sh sncfRecommendationUC $1