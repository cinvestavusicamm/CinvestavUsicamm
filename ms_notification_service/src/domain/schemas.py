from pydantic import BaseModel


class EmailNotification(BaseModel):
    to: str
    subject: str
    body: str


class PushNotification(BaseModel):
    device_id: str
    title: str
    body: str
