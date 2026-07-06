"""
Monitor de cambios en la página de caps de Australia WHV 462
Avisa por email cuando cambia el campo pageModified

USO:
1. Instala dependencias:   pip install requests beautifulsoup4
2. Configura tu email abajo en CONFIGURACION
3. Ejecuta:                python monitor_australia_caps.py
4. Déjalo corriendo (o añádelo a cron / Task Scheduler)
"""

import requests
import smtplib
import time
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# ============================================================
#  CONFIGURACION — cambia estos valores
# ============================================================

EMAIL_ORIGEN     = "alexfuegomez@gmail.com"   # Tu Gmail
EMAIL_DESTINO    = "alexfuegomez@gmail.com"   # Donde recibes el aviso (puede ser el mismo)
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"    # App Password de Google (ver instrucciones abajo)

INTERVALO_MINUTOS = 30                         # Cada cuántos minutos comprueba la página
VALOR_ACTUAL      = "3 July 2026"             # Valor actual — cambia si ya sabes el nuevo

URL = "https://immi.homeaffairs.gov.au/what-we-do/whm-program/status-of-country-caps"
ARCHIVO_ESTADO = "ultimo_valor.json"

# ============================================================
#  FUNCIONES
# ============================================================

def obtener_valor_pagina():
    """Obtiene el valor actual del span pageModified en la página"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Busca el span con id pageModified
        elemento = soup.find(id="pageModified")
        
        if elemento:
            return elemento.get_text(strip=True)
        
        # Si no lo encuentra por id, busca por clase o texto cercano
        elemento = soup.find("span", {"id": "pageModified"})
        if elemento:
            return elemento.get_text(strip=True)
            
        return None
        
    except requests.RequestException as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error al acceder a la página: {e}")
        return None


def cargar_ultimo_valor():
    """Carga el último valor guardado en disco"""
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r") as f:
            data = json.load(f)
            return data.get("valor")
    return VALOR_ACTUAL


def guardar_valor(valor):
    """Guarda el valor actual en disco"""
    with open(ARCHIVO_ESTADO, "w") as f:
        json.dump({"valor": valor, "ultima_comprobacion": datetime.now().isoformat()}, f)


def enviar_email(valor_anterior, valor_nuevo):
    """Envía email de aviso cuando detecta un cambio"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🇦🇺 CAMBIO DETECTADO — Australia WHV 462 caps"
        msg["From"]    = EMAIL_ORIGEN
        msg["To"]      = EMAIL_DESTINO

        cuerpo = f"""
¡Se ha detectado un cambio en la página de caps de Australia!

URL: {URL}

Valor anterior: {valor_anterior}
Valor nuevo:    {valor_nuevo}

Fecha/hora detección: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Entra ahora en ImmiAccount y verifica si el cap de España está abierto:
https://immi.homeaffairs.gov.au/what-we-do/whm-program/status-of-country-caps

Si España aparece como OPEN, envía tu solicitud inmediatamente.
https://online.immi.gov.au/ola/app

¡Suerte Alex! 🚀
"""
        msg.attach(MIMEText(cuerpo, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ORIGEN, GMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_ORIGEN, EMAIL_DESTINO, msg.as_string())
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Email enviado a {EMAIL_DESTINO}")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error al enviar email: {e}")


def monitorizar():
    """Bucle principal de monitorización"""
    print("=" * 55)
    print("🇦🇺 Monitor Australia WHV 462 — Caps")
    print("=" * 55)
    print(f"URL:              {URL}")
    print(f"Intervalo:        cada {INTERVALO_MINUTOS} minutos")
    print(f"Aviso a:          {EMAIL_DESTINO}")
    print(f"Valor a detectar: cambio desde '{VALOR_ACTUAL}'")
    print("=" * 55)
    print("Iniciando... (Ctrl+C para detener)\n")

    ultimo_valor = cargar_ultimo_valor()

    while True:
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        valor_actual = obtener_valor_pagina()

        if valor_actual is None:
            print(f"[{ahora}] ⚠️  No se pudo obtener el valor. Reintentando en {INTERVALO_MINUTOS} min...")
        elif valor_actual != ultimo_valor:
            print(f"[{ahora}] 🚨 CAMBIO DETECTADO: '{ultimo_valor}' → '{valor_actual}'")
            enviar_email(ultimo_valor, valor_actual)
            guardar_valor(valor_actual)
            ultimo_valor = valor_actual
        else:
            print(f"[{ahora}] ✓ Sin cambios — valor: '{valor_actual}'")

        time.sleep(INTERVALO_MINUTOS * 60)


# ============================================================
#  INICIO
# ============================================================

if __name__ == "__main__":
    monitorizar()
