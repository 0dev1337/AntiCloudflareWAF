from pydantic import BaseModel


class WafSolveRequest(BaseModel):
    domain: str

