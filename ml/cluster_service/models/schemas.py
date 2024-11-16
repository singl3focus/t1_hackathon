from pydantic import BaseModel
from typing import List, Dict, Any


class InputData(BaseModel):
    data: List[Dict[str, Any]]
