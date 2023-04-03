from .base_recommendation import BaseRecommendation
from resources.rte.rtegrid2op_poc_simulator.assistantManager import AgentManager


class RTEManager(AgentManager, BaseRecommendation):

    def get_recommendation(self, request_args):
        self.recommandate(request_args.get("context", {}))
        parades = self.getlistOfParadeInfo()
        return {"ia_recommendation": parades}
