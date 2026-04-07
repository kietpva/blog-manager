import logging

from fastapi import APIRouter, Depends, Request, Response, status
from svix.webhooks import Webhook, WebhookVerificationError

from app.core.config import settings
from app.core.constants import ClerkEventEnum
from app.dependencies.users import get_user_service
from app.modules.users.schemas import UserCreate, UserUpdateByWebhooks
from app.modules.users.services import UserService

secret = settings.CLERK_WEBHOOK_SECRET

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/clerk", status_code=status.HTTP_204_NO_CONTENT)
async def clerk_webhook(
    request: Request,
    response: Response,
    service: UserService = Depends(get_user_service),
):
    """
    Clerk webhook handler
    """
    payload = await request.body()
    headers = request.headers

    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        event = wh.verify(payload, headers)
    except WebhookVerificationError as e:
        logging.info("❌ Webhook verify failed:", str(e))
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    # Handle event
    event_type = event.get("type")
    data = event.get("data", {})

    auth_id = data.get("id")
    if not auth_id:
        return

    emails = data.get("email_addresses", [])

    email = emails[0].get("email_address")
    first_name = data.get("first_name") or ""
    last_name = data.get("last_name") or ""
    is_active = data.get("banned") or False

    # Clerk may provide `event["type"]` either as a string (e.g. "user.created")
    # or as an Enum member depending on the caller/test.
    normalized_event_type = (
        event_type.value if hasattr(event_type, "value") else event_type
    )

    if normalized_event_type == ClerkEventEnum.USER_CREATED.value:
        service.create(
            UserCreate(
                auth_id=auth_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active,
            )
        )

    if normalized_event_type == ClerkEventEnum.USER_UPDATED.value:
        service.update_by_webhooks(
            auth_id,
            UserUpdateByWebhooks(
                first_name=first_name,
                last_name=last_name,
                is_active=not is_active,
            ),
        )

    return
