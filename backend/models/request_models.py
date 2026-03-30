from pydantic import BaseModel
from typing import Literal

class TranspileRequest(BaseModel):
    source_code: str
    source_lang: Literal["python"] = "python"
    target_lang: Literal["cpp", "javascript"]
