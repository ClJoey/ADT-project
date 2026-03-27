import pandas as pd
import re

# CONVERSIÓN TIEMPO
def tiempo_a_segundos(texto):
    if pd.isna(texto) or str(texto).strip() == "" or "No Aplica" in str(texto):
        return 0
    t = str(texto).replace(" ", "")
    try:
        signo = -1 if t.startswith("-") else 1
        limpio = t.replace("+", "").replace("-", "")
        partes = limpio.split(':')
        return signo * (int(partes[0]) * 3600 + int(partes[1]) * 60 + int(partes[2]))
    except:
        return 0


# RANGO COLACIÓN
def calcular_duracion_rango(texto_rango):
    if pd.isna(texto_rango) or "-" not in str(texto_rango):
        return 0
    try:
        partes = str(texto_rango).split("-")
        inicio = tiempo_a_segundos(partes[0].strip())
        fin = tiempo_a_segundos(partes[1].strip())
        return abs(fin - inicio)
    except:
        return 0


# FORMATO TEXTO
def segundos_a_texto(segundos):
    signo = "-" if segundos < 0 else "+"
    abs_seg = abs(segundos)
    h, m = divmod(abs_seg, 3600)
    m, s = divmod(m, 60)
    return f"{signo} {int(h):02d}:{int(m):02d}:{int(s):02d}"


# FUNCIÓN CLAVE (maneja turnos nocturnos)
def calcular_duracion(inicio, fin):
    if fin < inicio:
        return (fin + 86400) - inicio
    return fin - inicio


# AUDITORÍA PRINCIPAL
def auditar_excel_final(ruta_excel):

    df = pd.read_excel(ruta_excel, header=None)

    errores = []

    suma_pactada = 0
    suma_real = 0
    suma_faltante = 0
    suma_extra = 0

    for i, fila in df.iterrows():

        fecha_str = str(fila[0])

        # FILAS DIARIAS
        if re.match(r'\d{2}/\d{2}/\d{2}', fecha_str):

            colacion = calcular_duracion_rango(fila[6])

            # --- PACTADA ---
            p_in = tiempo_a_segundos(fila[1])
            p_out = tiempo_a_segundos(fila[2])

            if p_in > 0 and p_out > 0:
                pactada = calcular_duracion(p_in, p_out) - colacion
            else:
                pactada = 0

            suma_pactada += pactada

            # --- REAL ---
            r_in = tiempo_a_segundos(fila[3])
            r_out = tiempo_a_segundos(fila[5])

            if r_in > 0 and r_out > 0:
                real = calcular_duracion(r_in, r_out) - colacion
            else:
                real = 0

            suma_real += real

            # --- FALTANTE / EXTRA ---
            faltante = tiempo_a_segundos(fila[9])
            extra = tiempo_a_segundos(fila[11])

            suma_faltante += faltante
            suma_extra += extra

        # TOTAL SEMANAL (solo los válidos)
        if "Total Semanal" in fecha_str and str(fila[1]).strip() != "00:00:00":

            # COLUMNAS CORRECTAS
            total_pactada_excel = tiempo_a_segundos(fila[1])
            total_real_excel = tiempo_a_segundos(fila[3])
            total_balance_excel = tiempo_a_segundos(fila[9])

            total_balance_calculado = suma_faltante + suma_extra

            # VALIDACIONES
            if abs(suma_pactada - total_pactada_excel) > 120:
                errores.append(
                    f"PACTADA ERROR | Esperado: {segundos_a_texto(suma_pactada)} | Excel: {segundos_a_texto(total_pactada_excel)}"
                )

            if abs(suma_real - total_real_excel) > 120:
                errores.append(
                    f"REAL ERROR | Esperado: {segundos_a_texto(suma_real)} | Excel: {segundos_a_texto(total_real_excel)}"
                )

            if abs(total_balance_calculado - total_balance_excel) > 120:
                errores.append(
                    f"BALANCE ERROR | Esperado: {segundos_a_texto(total_balance_calculado)} | Excel: {segundos_a_texto(total_balance_excel)}"
                )

            # RESET
            suma_pactada = 0
            suma_real = 0
            suma_faltante = 0
            suma_extra = 0

    if errores:
        return False, errores

    return True, []