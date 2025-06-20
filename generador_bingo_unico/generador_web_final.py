import random
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import streamlit as st
import io
import base64
import os

# Cargar historial de cartones
CARTONES_PATH = "cartones_usados.json"
if not os.path.exists(CARTONES_PATH):
    with open(CARTONES_PATH, "w") as f:
        json.dump({}, f)

with open(CARTONES_PATH, "r") as f:
    historial = json.load(f)

st.markdown("<h1 style='text-align: center;'>🎯 Bingos Dany - Generador de Cartones Únicos</h1>", unsafe_allow_html=True)

def generar_carton():
    columnas = {
        'B': random.sample(range(1, 16), 5),
        'I': random.sample(range(16, 31), 5),
        'N': random.sample(range(31, 46), 5),
        'G': random.sample(range(46, 61), 5),
        'O': random.sample(range(61, 76), 5),
    }
    columnas['N'][2] = 'FREE'
    return columnas

def carton_a_str(columnas):
    return str([columnas['B'], columnas['I'], columnas['N'], columnas['G'], columnas['O']])

def dibujar_marco_carnaval(c, width, height):
    colores = [colors.red, colors.green, colors.blue, colors.orange, colors.purple]
    grosor = 6
    secciones = 10
    ancho = (width - 40) / secciones
    alto = (height - 40) / secciones

    for i in range(secciones):
        c.setLineWidth(grosor)
        c.setStrokeColor(colores[i % len(colores)])
        # arriba
        c.line(20 + i * ancho, height - 20, 20 + (i + 1) * ancho, height - 20)
        # abajo
        c.line(20 + i * ancho, 20, 20 + (i + 1) * ancho, 20)
        # izquierda
        c.line(20, 20 + i * alto, 20, 20 + (i + 1) * alto)
        # derecha
        c.line(width - 20, 20 + i * alto, width - 20, 20 + (i + 1) * alto)

def dibujar_4_cartones_en_una_hoja(c, carton_id_base, columnas_list, comprador):
    width, height = letter
    cell_size = 38
    margen_superior = 60
    margen_lateral = 40
    espaciado_horizontal = 30
    espaciado_vertical = 30

    letras = ['B', 'I', 'N', 'G', 'O']

    # Marco carnaval
    dibujar_marco_carnaval(c, width, height)

    # Título decorativo
    c.setFont("Times-BoldItalic", 22)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 40, "🎉 Bingos Dany 🎉")

    posiciones = [
        (margen_lateral, height / 2 + espaciado_vertical / 2),
        (width / 2 + espaciado_horizontal / 2, height / 2 + espaciado_vertical / 2),
        (margen_lateral, margen_superior),
        (width / 2 + espaciado_horizontal / 2, margen_superior)
    ]

    for i, columnas in enumerate(columnas_list):
        x_offset, y_offset = posiciones[i]
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.black)
        c.drawCentredString(x_offset + cell_size * 2.5, y_offset + cell_size * 5.5, f"CARTÓN {carton_id_base}-{i+1}")

        c.setFont("Helvetica-Bold", 8)
        for j, letra in enumerate(letras):
            c.drawCentredString(x_offset + j * cell_size + cell_size / 2, y_offset + cell_size * 5.2, letra)

        c.setLineWidth(0.5)
        c.setFont("Helvetica", 7)
        for col, letra in enumerate(letras):
            for fila in range(5):
                y = y_offset + (4 - fila) * cell_size
                c.rect(x_offset + col * cell_size, y, cell_size, cell_size)
                valor = columnas[letra][fila]
                if valor == 'FREE':
                    c.setFillColor(colors.red)
                    c.drawCentredString(x_offset + col * cell_size + cell_size / 2, y + cell_size / 2 - 3, "FREE")
                    c.setFillColor(colors.black)
                else:
                    c.drawCentredString(x_offset + col * cell_size + cell_size / 2, y + cell_size / 2 - 3, str(valor))

    # Nombre grande al pie
    if comprador:
        c.setFont("Times-BoldItalic", 22)
        c.setFillColor(colors.darkblue)
        c.drawCentredString(width / 2, 30, f"👤 {comprador.upper()}")
    c.showPage()

# ==== INTERFAZ ====
numeros_texto = st.text_input("Escribe los números de cartones separados por coma (ej: 5,11,25,33):")
archivo_nombre = st.text_input("Escribe el nombre del archivo PDF a generar (sin extensión):")
comprador = st.text_input("Nombre del comprador que aparecerá en el PDF:")

if st.button("Generar Cartones"):
    try:
        numeros = [num.strip() for num in numeros_texto.split(",") if num.strip()]
        usados = [num for num in numeros if any(k.startswith(num + '-') for k in historial)]

        if usados:
            st.error(f"❌ Los siguientes números de cartón ya fueron utilizados: {', '.join(usados)}")
        else:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)

            for carton_id in numeros:
                cartones_en_hoja = []
                subindice = 1
                intentos = 0

                while len(cartones_en_hoja) < 4 and intentos < 200:
                    columnas = generar_carton()
                    clave = carton_a_str(columnas)
                    intentos += 1

                    if clave not in [carton_a_str(h) for h in historial.values()] and clave not in [carton_a_str(h) for h in cartones_en_hoja]:
                        cartones_en_hoja.append(columnas)
                        historial[f"{carton_id}-{subindice}"] = columnas
                        subindice += 1

                if len(cartones_en_hoja) == 4:
                    dibujar_4_cartones_en_una_hoja(c, carton_id, cartones_en_hoja, comprador)
                else:
                    st.warning(f"⚠️ No se pudieron generar 4 cartones únicos para el número {carton_id}.")

            c.save()
            buffer.seek(0)
            b64_pdf = base64.b64encode(buffer.read()).decode()

            with open(CARTONES_PATH, "w") as f:
                json.dump(historial, f)

            st.success(f"✅ Archivo generado correctamente con {len(numeros)} páginas.")
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{archivo_nombre.strip()}.pdf">📥 Descargar PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al generar los cartones: {e}")
