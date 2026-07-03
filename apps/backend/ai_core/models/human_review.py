from typing import Optional

from pydantic import BaseModel


class HumanReview(BaseModel):

    required: bool = False

    reason: Optional[str] = None

    reviewer: Optional[str] = None

    approved: Optional[bool] = None