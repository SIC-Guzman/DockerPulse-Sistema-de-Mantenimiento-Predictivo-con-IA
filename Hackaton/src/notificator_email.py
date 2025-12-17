import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "hakicro@gmail.com"       
EMAIL_PASS = "dmmh ynfv qxyu guuc"   
EMAIL_TO = "3617319650101@ingenieria.usac.edu.gt"  

def enviar_alerta_html(container_name, cpu_val, motivo="Riesgo IA Detectado"):
    try:
        msg = MIMEMultipart()
        msg['From'] = "DockerPulse Sentinel <" + EMAIL_SENDER + ">"
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"🚨 ALERTA CRÍTICA: {container_name} Reiniciado"

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # HTML PROFESIONAL
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #d32f2f; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">🚨 INCIDENTE DETECTADO</h1>
                    <p style="margin: 5px 0 0;">DockerPulse Sentinel System</p>
                </div>
                
                <div style="padding: 20px;">
                    <p>El sistema de Inteligencia Artificial ha ejecutado un protocolo de <strong>Self-Healing</strong>.</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <tr style="background-color: #f2f2f2;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Servicio Afectado:</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: #d32f2f; font-weight: bold;">{container_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Uso de CPU:</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{cpu_val}%</td>
                        </tr>
                        <tr style="background-color: #f2f2f2;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Causa:</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{motivo}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Acción Tomada:</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd; color: green;">✅ REINICIO AUTOMÁTICO</td>
                        </tr>
                        <tr style="background-color: #f2f2f2;">
                            <td style="padding: 10px; border: 1px solid #ddd;"><strong>Hora:</strong></td>
                            <td style="padding: 10px; border: 1px solid #ddd;">{fecha}</td>
                        </tr>
                    </table>

                    <p style="margin-top: 20px; font-size: 12px; color: #666;">
                        Este es un mensaje automático generado por el motor de IA. No responder.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, 'html'))

        # Conexión al servidor
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASS)
        server.sendmail(EMAIL_SENDER, EMAIL_TO, msg.as_string())
        server.quit()

        print(f"📧 Correo de alerta enviado exitosamente a {EMAIL_TO}")
        return True

    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
        return False