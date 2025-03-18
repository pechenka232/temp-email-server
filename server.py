import asyncio
import json
import datetime
from fastapi import FastAPI
from aiosmtpd.controller import Controller
from starlette.websockets import WebSocket
import uvicorn

app = FastAPI()

# Храним временные email-адреса
emails = {}

class MailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if "@" in address:
            emails[address] = []
            return "250 OK"
        return "550 No such user"

    async def handle_DATA(self, server, session, envelope):
        message = envelope.content.decode('utf-8')
        for rcpt in envelope.rcpt_tos:
            if rcpt in emails:
                emails[rcpt].append({"time": datetime.datetime.now(), "message": message})
        return "250 Message accepted"

# Запускаем SMTP-сервер
def run_smtp_server():
    controller = Controller(MailHandler(), hostname="127.0.0.1", port=1025)
    controller.start()
    print("📡 SMTP-сервер запущен на 127.0.0.1:1025")

# Очистка старых писем (удаляем письма старше 24 часов)
async def cleanup_old_emails():
    while True:
        now = datetime.datetime.now()
        for email in list(emails.keys()):
            emails[email] = [msg for msg in emails[email] if (now - msg["time"]).seconds < 86400]
            if not emails[email]:
                del emails[email]
        await asyncio.sleep(3600)  # Проверяем раз в час

# WebSocket API для получения сообщений
@app.websocket("/ws/{email}")
async def websocket_endpoint(websocket: WebSocket, email: str):
    await websocket.accept()
    while True:
        if email in emails and emails[email]:
            await websocket.send_text(json.dumps(emails[email]))
            emails[email] = []  # Очищаем после отправки
        await asyncio.sleep(5)

# Главный асинхронный процесс
async def main():
    loop = asyncio.get_event_loop()
    smtp_task = loop.run_in_executor(None, run_smtp_server)
    cleanup_task = asyncio.create_task(cleanup_old_emails())

    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    api_task = uvicorn.Server(config).serve()

    await asyncio.gather(smtp_task, cleanup_task, api_task)

if __name__ == "__main__":
    asyncio.run(main())
