import requests
import time

url = "http://localhost:5013/graphql"
batch = [{"query": "query { systemUpdate }"} for _ in range(1)]

start = time.time()
try:
    response = requests.post(url, json=batch, timeout=20)  # timeout de 10 segundos
    end = time.time()
    print("Status:", response.status_code)
    print("Tiempo de respuesta:", end - start, "segundos")
except requests.exceptions.Timeout:
    end = time.time()
    print("El request excedió el tiempo de espera (timeout).")
    print("Tiempo transcurrido:", end - start, "segundos")
except Exception as e:
    end = time.time()
    print("Error durante el request:", e)
    print("Tiempo transcurrido:", end - start, "segundos")