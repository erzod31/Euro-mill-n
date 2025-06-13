import streamlit as st
import pandas as pd
import requests
from io import StringIO
from collections import Counter
import random
import datetime

st.set_page_config(page_title="EuroMillones Automático", page_icon="🎲", layout="centered")
st.title("Generador Automático de EuroMillones")

st.markdown("Se generan 5 combinaciones estadísticas posibles para el próximo sorteo.")

def elegir_ponderado(counter, cantidad):
    elementos = list(counter.keys())
    pesos = [counter[k] for k in elementos]
    seleccionados = set()
    while len(seleccionados) < cantidad:
        elegido = random.choices(elementos, weights=pesos, k=1)[0]
        seleccionados.add(elegido)
    return sorted(list(seleccionados))

def calcular_proxima_fecha(fecha_ultima):
    hoy = datetime.date.today()
    proxima = fecha_ultima + datetime.timedelta(days=1)
    while proxima.weekday() not in [1, 4] or proxima <= hoy:
        proxima += datetime.timedelta(days=1)
    return proxima

if st.button("Generar 5 series posibles"):
    with st.spinner("Procesando datos internos de los últimos 6 meses..."):
        try:
            URL_CSV = "https://www.loterias.com/archivos/euromillones.csv"
            r = requests.get(URL_CSV, timeout=10)
            r.raise_for_status()
            df = pd.read_csv(StringIO(r.text), sep=',', header=0, parse_dates=['Fecha'])
            df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
            fecha_ultima = df['Fecha'].max().date()
            fecha_inicio = fecha_ultima - pd.DateOffset(months=6)
            df_filtrado = df[df['Fecha'] >= fecha_inicio]
            numeros, estrellas = [], []
            for _, fila in df_filtrado.iterrows():
                numeros += [fila[f'Bola {i}'] for i in range(1, 6)]
                estrellas += [fila[f'Estrella {i}'] for i in range(1, 3)]
            conteo_numeros = Counter(numeros)
            conteo_estrellas = Counter(estrellas)
            proxima_fecha = calcular_proxima_fecha(fecha_ultima)
            st.info(f"**Próximo sorteo de EuroMillones:** {proxima_fecha.strftime('%A, %d/%m/%Y')}")
            st.success("¡Aquí tienes 5 series sugeridas!")
            for i in range(1, 6):
                nums_elegidos = elegir_ponderado(conteo_numeros, 5)
                estrellas_elegidas = elegir_ponderado(conteo_estrellas, 2)
                st.markdown(f"**Serie {i}:**  Números: `{nums_elegidos}`  |  Estrellas: `{estrellas_elegidas}`")
        except Exception as e:
            st.error(f"Ocurrió un error al procesar los datos:\n{str(e)}")
else:
    st.info("Presiona el botón para ver tus 5 posibles combinaciones.")

st.caption("Datos descargados automáticamente de https://www.loterias.com/archivos/euromillones.csv")
