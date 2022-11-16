from typing import List

from fastapi import APIRouter, FastAPI, HTTPException, Request
from pydantic import BaseModel

from service.api.exceptions import UserNotFoundError
from service.log import app_logger

AVAILABLE_MODELS = ("first",)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {
                "errors": [
                    {
                        "error_key": "http_exception",
                        "error_message": "Model not found",
                        "error_loc": None,
                    }
                ]
            }
        }


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    responses={
        200: {
            "model": RecoResponse,
            "description": "Computed recommendation",
        },
        404: {
            "model": HTTPError,
            "description": "Given recommendation model has been not found",
        },
    },
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail="Model not found")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    k_recs = request.app.state.k_recs
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
