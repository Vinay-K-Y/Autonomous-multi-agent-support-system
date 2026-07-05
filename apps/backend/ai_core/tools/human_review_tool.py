from ai_core.models.human_review import HumanReview
from ai_core.tools.base_tool import BaseTool


class HumanReviewTool(BaseTool):

    name = "human_review"

    def execute(
        self,
        required: bool,
        reason: str = "",
    ):

        return HumanReview(
            required=required,
            reason=reason if required else None,
        )