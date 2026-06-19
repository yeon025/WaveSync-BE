from pydantic import BaseModel


class ResonatorImageRequest(BaseModel):
    imageUrl: str
