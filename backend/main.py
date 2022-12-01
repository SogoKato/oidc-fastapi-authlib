from dataclasses import dataclass
from datetime import datetime
from logging import INFO, StreamHandler, getLogger
from typing import Optional

from authlib.integrations.starlette_client import OAuth, OAuthError
from authlib.jose import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseSettings
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse


class Settings(BaseSettings):
    oidc_client_id: str
    oidc_client_secret: str
    session_secret_key: str
    oidc_config_endpoint: str

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI()
app.add_middleware(
    SessionMiddleware, secret_key=settings.session_secret_key, https_only=True
)

oauth = OAuth()
oauth.register(
    name="auth0",
    server_metadata_url=settings.oidc_config_endpoint,
    client_id=settings.oidc_client_id,
    client_secret=settings.oidc_client_secret,
    client_kwargs={"scope": "openid profile"},
)

logger = getLogger(__name__)
ch = StreamHandler()
ch.setLevel(INFO)
logger.addHandler(ch)
logger.setLevel(INFO)


class UnauthenticatedError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="You are not authenticated.")


async def verify_token(id_token: str):
    jwks = await oauth.auth0.fetch_jwk_set()
    try:
        decoded_jwt = jwt.decode(s=id_token, key=jwks)
    except Exception:
        logger.exception("An error occurred while decoding jwt.")
        raise UnauthenticatedError()
    metadata = await oauth.auth0.load_server_metadata()
    if decoded_jwt["iss"] != metadata["issuer"]:
        raise UnauthenticatedError()
    if decoded_jwt["aud"] != settings.oidc_client_id:
        raise UnauthenticatedError()
    exp = datetime.fromtimestamp(decoded_jwt["exp"])
    if exp < datetime.now():
        raise UnauthenticatedError()
    return decoded_jwt


async def verify_user(request: Request):
    id_token = request.session.get("id_token")
    if id_token is None:
        raise UnauthenticatedError()
    decoded_jwt = await verify_token(id_token=id_token)
    user_id = decoded_jwt["sub"]
    user_repo = UserRepository()
    user = user_repo.select_by_user_id(user_id=user_id)
    if user is None:
        raise UnauthenticatedError()
    return user


@dataclass
class User:
    id: str
    name: str


class UserRepository:
    users: list[User] = []

    def select_by_user_id(self, user_id: str) -> Optional[User]:
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def insert(self, user: User) -> None:
        self.users.append(user)


@app.get("/api/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.auth0.authorize_redirect(request, redirect_uri)


@app.get("/api/auth")
async def auth(request: Request):
    try:
        token = await oauth.auth0.authorize_access_token(request)
    except OAuthError:
        logger.exception("An error occurred while verifying authorization response.")
        raise UnauthenticatedError()
    userinfo = token.get("userinfo")
    if not userinfo:
        raise ValueError()
    user_dict = dict(userinfo)
    user_repo = UserRepository()
    user_id = user_dict["sub"]
    name = user_dict["name"]
    user = user_repo.select_by_user_id(user_id=user_id)
    if user is None:
        user = User(id=user_id, name=name)
        user_repo.insert(user=user)
        logger.info(f"New user created! user_id={user.id} name={user.name}")
    else:
        logger.info(
            f"The user exists; skipped registration. user_id={user.id} name={user.name}"
        )
    request.session["id_token"] = token.get("id_token")
    return RedirectResponse(url="/")


@app.get("/api/logout")
async def logout(request: Request, user: User = Depends(verify_user)):
    logger.info(f"A user logged out: user_id={user.id} name={user.name}")
    request.session.pop("id_token")
    return RedirectResponse(url="/")


@app.get("/api/userinfo")
async def userinfo(request: Request, user: User = Depends(verify_user)):
    logger.info(f"Successful log in: user_id={user.id} name={user.name}")
    return {
        "userinfo": {
            "id": user.id,
            "name": user.name,
        }
    }


@app.get("/api/items")
async def list_items(user: User = Depends(verify_user)):
    logger.info(f"Successful log in: user_id={user.id} name={user.name}")
    return {
        "items": [
            {"name": "Teddy bear", "icon": "🧸", "price": 99},
            {"name": "Apple", "icon": "🍎", "price": 2},
            {"name": "Sushi", "icon": "🍣", "price": 200},
            {"name": "Bento", "icon": "🍱", "price": 50},
        ]
    }
