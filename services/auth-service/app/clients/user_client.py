import httpx

from app.config import settings

class UserProfileCreationException(Exception):
    pass

SERVICE_HEADERS = {
    "X-SERVICE-TOKEN" : settings.user_service_auth_token,
}

def create_user_profile(
    auth_user_id: str
) -> None:
    
    url = (
        f"{settings.user_service_url}"
        f"/api/v1/users/internal"
    )

    payload = {
        "auth_user_id": auth_user_id
    }

    try:
        response = httpx.post(
            url=url,
            json=payload,
            headers=SERVICE_HEADERS,
            timeout=5.0,
        )

    except httpx.HTTPError as exc:
        raise UserProfileCreationException(
            "failed to create user profile"
        ) from exc
    # response.raise_for_status()
    
