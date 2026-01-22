#!/usr/bin/env python3
"""
FK94 Security - Telegram Setup Script
Genera la session string para usar el bot de Truecaller

Uso:
    python setup_telegram.py
"""
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    print("=" * 50)
    print("FK94 Security - Setup de Telegram")
    print("=" * 50)
    print()
    print("Necesitás los datos de https://my.telegram.org")
    print()

    api_id = input("API_ID (número): ").strip()
    api_hash = input("API_HASH (string): ").strip()
    phone = input("Tu número de teléfono (ej: +5491155551234): ").strip()

    print()
    print("Conectando a Telegram...")

    client = TelegramClient(StringSession(), int(api_id), api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        print()
        print("📱 Te enviamos un código a Telegram")
        code = input("Código: ").strip()

        try:
            await client.sign_in(phone, code)
        except Exception as e:
            if "Two-step verification" in str(e) or "password" in str(e).lower():
                password = input("Tenés 2FA. Ingresá tu contraseña: ").strip()
                await client.sign_in(password=password)
            else:
                raise e

    session_string = client.session.save()
    await client.disconnect()

    print()
    print("=" * 50)
    print("✅ LISTO! Agregá esto a tu .env:")
    print("=" * 50)
    print()
    print(f"TELEGRAM_API_ID={api_id}")
    print(f"TELEGRAM_API_HASH={api_hash}")
    print(f"TELEGRAM_SESSION={session_string}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
