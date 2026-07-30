from ai_core.models.human_review import HumanReview
from ai_core.tools.base_tool import BaseTool


class HumanReviewTool(BaseTool):

    name = "human_review"
    description = "Escalates a request to a human agent."
    
    def execute(
        self,
        required: bool = True,
        reason: str = "",
    ):

        return HumanReview(
            required=required,
            reason=reason if required else None,
        )
