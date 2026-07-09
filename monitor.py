"""
Monitor WHV 462 - España
Busca el estado de Spain en la tabla de caps.
Si cambia de "paused" a cualquier otra cosa -> exit(1) -> GitHub Actions falla -> te manda email
"""

import requests
import os
import sys
from bs4 import BeautifulSoup

URL = "https://immi.homeaffairs.gov.au/what-we-do/whm-program/status-of-country-caps"
ARCHIVO_ESTADO = "ultimo_valor.txt"
VALOR_INICIAL  = "paused"


def obtener_estado_spain():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Busca la fila que contiene "Spain"
        for fila in soup.find_all("tr"):
            celdas = fila.find_all("td")
            if celdas and "Spain" in celdas[0].get_text():
                # El estado está en el span label dentro de la segunda celda
                span = celdas[1].find("span")
                if span:
                    return span.get_text(strip=True).replace("\u200b", "").strip()
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
    ultimo_valor = cargar_ultimo_valor()
    valor_actual = obtener_estado_spain()

    print(f"Estado guardado: '{ultimo_valor}'")
    print(f"Estado en web:   '{valor_actual}'")

    if valor_actual is None:
        print("No se pudo obtener el estado de Spain. Reintenta en el próximo ciclo.")
        sys.exit(0)  # No falla — puede ser error temporal de red

    if valor_actual != ultimo_valor:
        # Guarda el nuevo valor
        guardar_valor(valor_actual)
        # Falla con exit(1) -> GitHub te manda email automáticamente
        print(f"CAMBIO DETECTADO: '{ultimo_valor}' → '{valor_actual}'")
        print("Entra en ImmiAccount: https://online.immi.gov.au/ola/app")
        sys.exit(1)
    else:
        print(f"Sin cambios. Spain sigue: '{valor_actual}'")
        sys.exit(0)


if __name__ == "__main__":
    main()
