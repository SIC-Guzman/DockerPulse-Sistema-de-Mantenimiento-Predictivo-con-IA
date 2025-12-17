from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generar_pdf_incidente(container_name, cpu_val, riesgo_ia):
    # Crear carpeta reportes si no existe
    if not os.path.exists("reportes"):
        os.makedirs("reportes")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reportes/Incidente_{container_name}_{timestamp}.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Encabezado
    c.setFillColorRGB(0.8, 0, 0) # Rojo
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "REPORTE DE INCIDENTE CRÍTICO")
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "Generado automáticamente por DockerPulse AI")
    c.line(50, height - 90, 550, height - 90)

    # Datos del incidente
    y = height - 150
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Detalles del Evento:")
    
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(70, y, f"• Fecha y Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    y -= 25
    c.drawString(70, y, f"• Contenedor Afectado: {container_name}")
    
    y -= 25
    c.drawString(70, y, f"• Carga de CPU Registrada: {cpu_val}%")
    
    y -= 25
    c.drawString(70, y, f"• Nivel de Riesgo IA: {riesgo_ia}")

    # Acción tomada
    y -= 50
    c.setFillColorRGB(0, 0.5, 0) # Verde
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "ACCIÓN EJECUTADA: REINICIO AUTOMÁTICO (SELF-HEALING)")

    # Footer
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Este documento es evidencia oficial del sistema de monitoreo.")
    
    c.save()
    print(f"📄 PDF Generado: {filename}")
    return filename