"""
Monitor de cambios en la página de caps de Australia WHV 462
Versión para GitHub Actions — ejecuta una vez y termina
"""

import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://immi.homeaffairs.gov.au/what-we-do/whm-program/status-of-country-caps"
ARCHIVO_ESTADO = "ultimo_valor.txt"
VALOR_INICIAL  = "3 July 2026"


def obtener_valor_pagina():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        elemento = soup.find(id="pageModified")
        if elemento:
            return elemento.get_text(strip=True)
        return None
    except Exception as e:
        print(f"Error al acceder a la página: {e}")
        return None


def cargar_ultimo_valor():
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, "r") as f:
            return f.read().strip()
    return VALOR_INICIAL


def guardar_valor(valor):
    with open(ARCHIVO_ESTADO, "w") as f:
        f.write(valor)


def main():
    ahora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print(f"[{ahora}] Comprobando página...")

    ultimo_valor = cargar_ultimo_valor()
    valor_actual = obtener_valor_pagina()

    print(f"Último valor guardado: '{ultimo_valor}'")
    print(f"Valor actual en web:   '{valor_actual}'")

    github_output = os.environ.get("GITHUB_OUTPUT", "")

    if valor_actual is None:
        print("⚠️ No se pudo obtener el valor de la página.")
        if github_output:
            with open(github_output, "a") as f:
                f.write("cambio_detectado=false\n")
        return

    if valor_actual != ultimo_valor:
        print(f"🚨 CAMBIO DETECTADO: '{ultimo_valor}' → '{valor_actual}'")
        guardar_valor(valor_actual)
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"cambio_detectado=true\n")
                f.write(f"valor_anterior={ultimo_valor}\n")
                f.write(f"valor_nuevo={valor_actual}\n")
    else:
        print(f"✓ Sin cambios — valor: '{valor_actual}'")
        if github_output:
            with open(github_output, "a") as f:
                f.write("cambio_detectado=false\n")


if __name__ == "__main__":
    main()
