
import streamlit as st
import random
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

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

def crear_pdf(nombre_archivo, cartones, comprador, base_numeros):
    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    width, height = letter

    x_offsets = [50, 320]
    y_offsets = [height - 100, height - 400]

    index = 0
    numero_carton = 1

    for i in range(0, len(cartones), 4):
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.darkorange)
        c.drawCentredString(width/2, height - 30, "🎉 Bingos Dany 🎉")

        for fila_index, fila in enumerate(y_offsets):
            for columna_index, columna in enumerate(x_offsets):
                if index >= len(cartones):
                    break
                etiqueta = f"{base_numeros}-{numero_carton}"
                mostrar_arriba = fila_index == 0
                dibujar_carton(c, cartones[index], columna, fila, etiqueta, mostrar_arriba)
                numero_carton += 1
                index += 1

        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, 30, f"Comprador: {comprador}")
        c.showPage()

    c.save()

def dibujar_carton(c, carton, x, y, etiqueta, mostrar_arriba):
    ancho_celda = 55
    alto_celda = 55
    letras = ['B', 'I', 'N', 'G', 'O']

    if mostrar_arriba:
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + 125, y + 15, f"Cartón {etiqueta}")

    c.setFillColor(colors.whitesmoke)
    c.rect(x, y - alto_celda * 6, ancho_celda * 5, alto_celda * 6, fill=1)

    for i, letra in enumerate(letras):
        c.setFillColor(colors.darkblue)
        c.setFont("Helvetica-Bold", 22)
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

    if not mostrar_arriba:
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + 125, y - alto_celda * 6 - 10, f"Cartón {etiqueta}")

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
            total = len(cantidad_lista) * 4
            cartones_generados = generar_cartones_unicos(total)

            base_numeros = "_".join(map(str, cantidad_lista))
            nombre_archivo = f"{nombre_pdf}_{base_numeros}.pdf"
            crear_pdf(nombre_archivo, cartones_generados, nombre_comprador, base_numeros)

            with open(nombre_archivo, "rb") as file:
                st.download_button(label="📥 Descargar PDF", data=file, file_name=nombre_archivo)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
    else:
        st.warning("Por favor completa todos los campos.")
