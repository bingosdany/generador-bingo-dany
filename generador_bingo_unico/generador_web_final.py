
import streamlit as st
import random
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

CARTONES_PATH = "cartones_usados.json"

def generar_carton():
    columnas = {
        'B': random.sample(range(1, 16), 5),
        'I': random.sample(range(16, 31), 5),
        'N': random.sample(range(31, 46), 5),
        'G': random.sample(range(46, 61), 5),
        'O': random.sample(range(61, 76), 5)
    }
    columnas['N'][2] = 'FREE'
    return columnas

def carton_a_string(carton):
    return '-'.join(str(item) for col in ['B','I','N','G','O'] for item in carton[col])

def guardar_carton_usado(cadena):
    usados = cargar_cartones_usados()
    usados.append(cadena)
    with open(CARTONES_PATH, 'w') as f:
        json.dump(usados, f)

def cargar_cartones_usados():
    if os.path.exists(CARTONES_PATH):
        with open(CARTONES_PATH, 'r') as f:
            return json.load(f)
    return []

def generar_cartones_unicos(n):
    cartones = []
    usados = set(cargar_cartones_usados())
    intentos = 0
    while len(cartones) < n and intentos < n * 10:
        c = generar_carton()
        s = carton_a_string(c)
        if s not in usados:
            guardar_carton_usado(s)
            cartones.append(c)
        intentos += 1
    return cartones

def crear_pdf(nombre_archivo, cartones, comprador):
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.darkorange)
    c.drawCentredString(width/2, height - 40, "🎉 Bingos Dany 🎉")

    x_offsets = [30, 310]
    y_offsets = [height - 140, height - 440]

    index = 0
    for fila in y_offsets:
        for columna in x_offsets:
            if index >= len(cartones):
                break
            dibujar_carton(c, cartones[index], columna, fila)
            index += 1

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, 40, f"Comprador: {comprador}")

    c.showPage()
    c.save()

def dibujar_carton(c, carton, x, y):
    ancho_celda = 50
    alto_celda = 50
    letras = ['B', 'I', 'N', 'G', 'O']

    c.setFillColor(colors.whitesmoke)
    c.rect(x, y - alto_celda * 6, ancho_celda * 5, alto_celda * 6, fill=1)

    for i, letra in enumerate(letras):
        c.setFillColor(colors.darkblue)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(x + i * ancho_celda + ancho_celda / 2, y, letra)

    c.setFont("Helvetica", 16)
    for col_index, letra in enumerate(letras):
        for row_index in range(5):
            valor = carton[letra][row_index]
            if valor == 'FREE':
                c.setFillColor(colors.lightgrey)
                c.rect(x + col_index * ancho_celda, y - (row_index + 1) * alto_celda, ancho_celda, alto_celda, fill=1)
                c.setFillColor(colors.black)
            c.drawCentredString(x + col_index * ancho_celda + ancho_celda / 2,
                                y - (row_index + 1) * alto_celda + alto_celda / 3, str(valor))

# INTERFAZ STREAMLIT
st.markdown("<h1 style='text-align: center; color: orange;'>🎉 Generador de Cartones - Bingos Dany 🎉</h1>", unsafe_allow_html=True)

if st.button("🧹 Limpiar historial de cartones usados"):
    with open(CARTONES_PATH, "w") as f:
        json.dump([], f)
    st.success("✅ Historial de cartones limpiado. Puedes generar nuevos cartones sin restricciones.")

cantidad = st.text_input("Escribe los números de cartones que quieres generar separados por coma (ej: 1,2,3):")
nombre_pdf = st.text_input("Nombre del archivo PDF:", "cartones_bingo")
nombre_comprador = st.text_input("Nombre del comprador:")

if st.button("Generar Cartones"):
    if cantidad and nombre_pdf and nombre_comprador:
        try:
            cantidad_lista = [int(x.strip()) for x in cantidad.split(',') if x.strip().isdigit()]
            total = len(cantidad_lista)
            cartones_generados = generar_cartones_unicos(total)
            crear_pdf(f"{nombre_pdf}.pdf", cartones_generados, nombre_comprador)
            with open(f"{nombre_pdf}.pdf", "rb") as file:
                st.download_button(label="📥 Descargar PDF", data=file, file_name=f"{nombre_pdf}.pdf")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
    else:
        st.warning("Por favor completa todos los campos.")

