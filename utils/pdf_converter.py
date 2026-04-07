import pdfkit
import os
import platform

def convertir_html_a_pdf(directorio_reportes):
    # Configuración de la ruta de wkhtmltopdf según el sistema
    if platform.system() == "Windows":
        # Ajusta esta ruta a donde lo instalaste en tu PC
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    else:
        # En GitHub Actions (Linux) ya está en el PATH tras instalarlo
        config = pdfkit.configuration()

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'quiet': ''
    }

    print("🚀 Iniciando conversión a PDF...")
    
    for archivo in os.listdir(directorio_reportes):
        if archivo.endswith(".html"):
            ruta_html = os.path.join(directorio_reportes, archivo)
            ruta_pdf = ruta_html.replace(".html", ".pdf")
            
            try:
                pdfkit.from_file(ruta_html, ruta_pdf, options=options, configuration=config)
                print(f"  Convertido: {archivo} -> PDF")
            except Exception as e:
                print(f"  Error en {archivo}: {e}")

if __name__ == "__main__":
    convertir_html_a_pdf("reports")