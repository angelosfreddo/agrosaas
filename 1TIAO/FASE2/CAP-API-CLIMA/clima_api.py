import urllib.request
import json

def verificar_previsao_chuva(lat=-23.5505, lon=-46.6333):
    # Usando a API gratuita do Open-Meteo (mesma da Fase 1, sem necessidade de chave)
    # Busca a previsao de precipitacao para as proximas horas
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation_probability&forecast_days=1"
    
    print("==================================================")
    print(f"Consultando API Open-Meteo (Lat: {lat}, Lon: {lon})")
    print("==================================================")
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                probabilidades = data.get('hourly', {}).get('precipitation_probability', [])
                
                # Verifica a probabilidade nas proximas 12 horas
                proximas_horas = probabilidades[:12]
                max_prob = max(proximas_horas) if proximas_horas else 0
                
                print(f"Probabilidade maxima de chuva nas proximas 12 horas: {max_prob}%\n")
                
                if max_prob > 50:
                    print("[ALERTA CLIMATICO] Alta probabilidade de chuva!")
                    print("Acao recomendada: Suspender a irrigacao para economizar agua.")
                    print("--------------------------------------------------")
                    print("=> Digite '1' no Monitor Serial do Wokwi para informar o ESP32.")
                else:
                    print("[CLIMA ESTAVEL] Sem previsao de chuva significativa.")
                    print("Acao recomendada: Manter o sistema de irrigacao operando normalmente.")
                    print("--------------------------------------------------")
                    print("=> Digite '0' no Monitor Serial do Wokwi para liberar o sistema.")
            else:
                print("Erro na consulta a API HTTP:", response.status)
    except Exception as e:
        print(f"Erro na conexao com a API: {e}")

if __name__ == "__main__":
    verificar_previsao_chuva()
