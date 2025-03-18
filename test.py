import smtplib

sender = "test@local"
recipient = "user@local"
message = """Subject: Test Email\n\nHello! Это тестовое письмо."""

with smtplib.SMTP("127.0.0.1", 1025) as server:
    server.sendmail(sender, recipient, message)
print("✅ Письмо отправлено!")
