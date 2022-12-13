import os
import pickle
from datetime import timedelta

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from service.api.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    authenticate_user,
    create_access_token,
    get_user,
    users_db,
)
from service.api.exceptions import UserNotFoundError
from service.log import app_logger
from service.models import HTTPError, RecoResponse, Token, TokenData, User
from service.utils import read_config
from src.recommenders import LightFMWrapper, UserKNN

AVAILABLE_MODELS = (
    "most_popular",
    "userknn",
    "lightfm",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
router = APIRouter()
config_path = "config.yml"
config = read_config(config_path)
userknn_model = UserKNN(config)
lightfm_model = LightFMWrapper(config)

if os.path.isfile(config["most_popular"]["model_path"]):
    with open(config["most_popular"]["model_path"], "rb") as f:
        popular_model = pickle.load(f)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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
    current_user: User = Depends(get_current_user),
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail="Model not found")

    if user_id > 10 ** 9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    reco = []
    k_recs = request.app.state.k_recs
    if model_name == "most_popular":
        reco = popular_model.recommend([user_id], n=k_recs)[0].tolist()
    elif model_name == "userknn" and user_id in userknn_model.users_mapping:
        reco = userknn_model.recommend([user_id])
    elif (
        model_name == "userknn" and
        user_id not in userknn_model.users_mapping
    ):
        reco = userknn_model.recommend([user_id])
        reco = popular_model.recommend([user_id], n=k_recs)[0].tolist()
    elif model_name == "lightfm" and user_id in lightfm_model.users_mapping:
        reco = lightfm_model.recommend([user_id])
    elif (
        model_name == "lightfm" and
        user_id not in lightfm_model.users_mapping
    ):
        reco = popular_model.recommend([user_id], n=k_recs)[0].tolist()
    if len(reco) < 10:
        reco += popular_model.recommend([user_id], n=k_recs)[0].tolist()
        reco = list(set(reco))[:10]
    return RecoResponse(user_id=user_id, items=reco)


def add_views(current_app: FastAPI) -> None:
    current_app.include_router(router)
