"""application.services.report_builder
Constructor Universal de Reportes.
Renderiza HTML con soporte para identidad visual dinámica gubernamental
mediante inyección de base64 y esquemas de Pydantic.
"""
import os
import io
import base64
import logging
from datetime import datetime
from zoneinfo import ZoneInfo  # Asegura la zona horaria correcta sin importar el contenedor
import matplotlib
import matplotlib.pyplot as plt
from jinja2 import Template

# Configuración para evitar errores de GUI en servidores Linux
matplotlib.use('Agg')
logger = logging.getLogger("ms_reports.builder")

class ReportBuilder:
    def __init__(self):
        # Directorio persistente donde vivirán los logos de la USICAMM / Gobiernos
        self.assets_dir = "/srv/ms3_reports/static/assets/logos"

    def _get_logo_base64(self, institution_id: str) -> str:
        """
        FR3: Busca el logo institucional en el volumen de Docker.
        """
        target_path = os.path.join(self.assets_dir, f"{institution_id}.png")
        default_path = os.path.join(self.assets_dir, "default.png")
        
        file_to_read = target_path if os.path.exists(target_path) else default_path
        
        if os.path.exists(file_to_read):
            try:
                with open(file_to_read, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')
                    return f"data:image/png;base64,{encoded}"
            except Exception as e:
                logger.error(f"Error al convertir logo a base64 ({file_to_read}): {e}")
        else:
            logger.warning(f"No se encontró ni el logo {institution_id} ni el default.")
            
        return ""

    def _generate_bar_chart(self, chart_data: dict, style: dict, title: str) -> str:
        """Genera una gráfica de barras usando los colores institucionales inyectados."""
        try:
            plt.figure(figsize=(7, 3.5))
            labels = list(chart_data.keys())
            values = list(chart_data.values())
            
            colors = [style.get("primary_color", "#691C32"), style.get("secondary_color", "#BC955C"), "#D4C19C"]
            colors = (colors * (len(labels) // len(colors) + 1))[:len(labels)]
            
            plt.bar(labels, values, color=colors)
            plt.ylim(0, max(values) * 1.2 if values else 100) # Ajuste dinámico de altura
            plt.xticks(rotation=25, ha='right', fontsize=8)
            plt.title(title, fontsize=12, fontweight='bold')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            img_io = io.BytesIO()
            plt.tight_layout()
            plt.savefig(img_io, format='png', transparent=True)
            plt.close()
            img_io.seek(0)
            return base64.b64encode(img_io.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generando gráfica: {e}")
            return ""

    def build_universal_html(self, layout_schema: dict, institution_id: str = "default") -> str:
        """
        Ensambla el HTML basado estrictamente en el diseño ordenado por la IA.
        """
        style = layout_schema.get("style", {})
        header_data = layout_schema.get("header", {"title": "Reporte Oficial", "subtitle": "Sistema EscalafonIA"})
        
        for section in layout_schema.get("sections", []):
            if section.get("type") == "chart" and section.get("data"):
                section["base64_img"] = self._generate_bar_chart(
                    section["data"], style, section.get("title", "Métricas")
                )

        logo_data_uri = self._get_logo_base64(institution_id)
        
        # FIJADO: Forzamos la zona horaria de la Ciudad de México
        mx_tz = ZoneInfo("America/Mexico_City")
        current_date = datetime.now(mx_tz).strftime("%d/%m/%Y %H:%M")

        html_template = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <style>
                @page { size: letter; margin: 2cm; }
                :root {
                    --primary: {{ style.primary_color | default('#691C32') }};
                    --secondary: {{ style.secondary_color | default('#BC955C') }};
                }
                body { 
                    font-family: Arial, sans-serif; color: #333; line-height: 1.5; position: relative;
                }
                
                .header { 
                    display: flex; align-items: center; justify-content: center;
                    border-bottom: 3px solid var(--primary); padding-bottom: 15px; margin-bottom: 20px;
                    text-align: center;
                }
                .logo { height: 70px; margin-right: 20px; object-fit: contain; }
                .header-text h1 { color: var(--primary); margin: 0; font-size: 22px; text-transform: uppercase; }
                .header-text h2 { color: #555; font-size: 14px; margin: 5px 0 0 0; }
                
                .section-title { color: var(--secondary); border-bottom: 1px solid var(--secondary); margin-top: 20px; padding-bottom: 5px; }
                
                .kv-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: rgba(255,255,255,0.85); }
                .kv-table td { padding: 8px; border-bottom: 1px solid #eee; }
                .kv-table td:first-child { font-weight: bold; width: 35%; color: #555; }
                
                .text-content { background-color: rgba(249,249,249,0.85); padding: 15px; border-left: 4px solid var(--primary); margin-top: 10px; text-align: justify; }
                
                .chart-container { text-align: center; margin-top: 20px; background: rgba(255,255,255,0.85); padding: 10px; border-radius: 8px; }
                .chart-container img { max-width: 100%; height: auto; }
                
                .footer { margin-top: 40px; font-size: 10px; color: #777; text-align: justify; border-top: 1px solid #ddd; padding-top: 10px; }
                .footer-flex { display: flex; justify-content: space-between; }
            </style>
        </head>
        <body>
            <div class="header">
                {% if logo_uri %}
                <img src="{{ logo_uri }}" class="logo" alt="Logo Institucional">
                {% endif %}
                <div class="header-text">
                    <h1>{{ header.title }}</h1>
                    <h2>{{ header.subtitle }}</h2>
                </div>
            </div>

            {% for section in sections %}
                <h3 class="section-title">{{ section.title }}</h3>
                
                {% if section.type == 'key_value' %}
                <table class="kv-table">
                    {% for key, value in section.data.items() %}
                    <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
                    {% endfor %}
                </table>
                {% elif section.type == 'text' %}
                <div class="text-content">
                    {{ section.content }}
                </div>
                {% elif section.type == 'chart' and section.base64_img %}
                <div class="chart-container">
                    <img src="data:image/png;base64,{{ section.base64_img }}" alt="Gráfica">
                </div>
                {% endif %}
            {% endfor %}

            <div class="footer">
                <div class="footer-flex">
                    <span><strong>AVISO LEGAL:</strong> {{ footer_text }}</span>
                    <span>Generado el: {{ date }}</span>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        return template.render(
            header=header_data,
            sections=layout_schema.get("sections", []),
            style=style,
            logo_uri=logo_data_uri,
            date=current_date,
            footer_text=layout_schema.get("footer_text", "Documento generado por EscalafonIA.")
        )