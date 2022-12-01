# oidc-fastapi-authlib
Sample implementation for OIDC with FastAPI and Authlib.

## About

This is a sample implementation for OpenID Connect with Python, FastAPI and Authlib.

![overview](https://www.plantuml.com/plantuml/png/PL5BIyD04BxlhnXxaFOWZO-JYBIqHGAbMLBimTisEzQbSIVkGzHVxsow8j5BmlVulfb9PZue5-9hArGJoC7ZTbM3yX0zEY2d-NbPY3rzm8YLNRbOmRYMav7eE6OQqoaRO2ldsNjL38IvBBDmNGYq6hXeO1XL7Tfo2TBHkqc-SSNbQO5AvkHD8VfbBkxxERUmQ4rpX7Nr0EK6zZ44ie8LDgHvR9YgpanREXWhc4Xy9PcUn_2oWHhV8lfmwhmRQkVz-qambSj-KxuZwt6S83dpfO8X2mlIE1aCsQOh_vi6bJM6w2oefa7l8T0H6N2iN9v0Bipk7Jhp_FbNpDzY-dDvEeVncWvWBFZ8tQXHduaPMis_zni0)

It uses...
* Authorization Code Flow
* Cookie to store ID token
  * HttpOnly: true, SameSite: Lax, Secure: true
* nginx for path routing  
  ![architecture](https://www.plantuml.com/plantuml/png/SoWkIImgAStDuKfCBialKWWDTWrII2nMA2rEBU9AB4hEoCnDB4bLK2v9JSx8oy_9JwzKo4lFpAjGiB41gYZBJ4wriyEXpZ70amXLIXuXlZxwpi71-bx1IY2RWGugoKn6qGboZ8Ak7THcAuMWrCBIrE8IBWXV5oW3j0iehfzOa8aGX9e44kToICrB0NeI0000)

Related post (Japanese): [よくあるSPA+API構成でのOpenID Connectクライアント実装](https://sogo.dev/posts/2022/12/openid-connect-fastapi)

## Getting Started

### Prerequisites
* docker / docker compose
* Some OpenID Provider
  * Set Redirect URI (Allowed Callback URLs) as `http://localhost:8080/api/auth`

Fill `.env` with each value below.
* Client ID
* Client Secret
* OpenID Configuration Endpoint

### Run

```sh
docker compose build
docker compose up
```

Open [http://localhost:8080/](http://localhost:8080/) in your browser and try it out!

![Log in](/docs/images/oidc_log_in.gif)
