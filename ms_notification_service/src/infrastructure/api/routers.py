from fastapi import APIRouter

from src.domain.schemas import EmailNotification, PushNotification

router = APIRouter(tags=["Notificaciones"])

@router.post("/notificaciones/email")
async def send_email(payload: EmailNotification):
    return {"status": "ok", "channel": "email", "to": payload.to, "message": "Correo enviado"}

@router.post("/notificaciones/push")
async def send_push(payload: PushNotification):
    return {"status": "ok", "channel": "push", "device_id": payload.device_id, "message": "NotificaciÃ³n enviada"}
