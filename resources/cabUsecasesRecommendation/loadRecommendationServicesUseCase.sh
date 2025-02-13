cd "$(dirname "${BASH_SOURCE[0]}")"

 ./createRecommendationUsecase.sh PowerGridRecommendationUC $1
 ./createRecommendationUsecase.sh ATMRecommendationUC $1
 ./createRecommendationUsecase.sh RailwayRecommendationUC $1