import csv
import io
import json
from datetime import datetime
from flask import make_response, send_file
import tempfile
import os

def export_to_csv(data, filename=None):
    """
    Exporta dados para formato CSV
    
    Args:
        data: Lista de dicionários com os dados a serem exportados
        filename: Nome do arquivo (opcional)
        
    Returns:
        Flask Response com o arquivo CSV para download
    """
    if not data:
        return None
        
    # Criar buffer de memória para o CSV
    output = io.StringIO()
    
    # Obter cabeçalhos do primeiro item
    fieldnames = data[0].keys()
    
    # Criar writer CSV
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    # Escrever dados
    for row in data:
        writer.writerow(row)
        
    # Preparar resposta
    output.seek(0)
    
    # Gerar nome de arquivo, se não fornecido
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.csv"
    
    # Criar resposta HTTP
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"
    
    return response

def export_to_excel(data, filename=None):
    """
    Exporta dados para formato Excel
    
    Args:
        data: Lista de dicionários com os dados a serem exportados
        filename: Nome do arquivo (opcional)
        
    Returns:
        Flask Response com o arquivo Excel para download
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Pandas é necessário para exportar para Excel. Instale com 'pip install pandas openpyxl'.")
    
    if not data:
        return None
    
    # Converter dados para DataFrame
    df = pd.DataFrame(data)
    
    # Criar buffer para o arquivo Excel
    output = io.BytesIO()
    
    # Salvar DataFrame no buffer como Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
        
    # Preparar resposta
    output.seek(0)
    
    # Gerar nome de arquivo, se não fornecido
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.xlsx"
    
    # Criar resposta HTTP
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def export_to_pdf(data, template_html=None, filename=None):
    """
    Exporta dados para PDF usando template HTML
    
    Args:
        data: Dados a serem exportados (dict ou list)
        template_html: Template HTML para renderização (opcional)
        filename: Nome do arquivo (opcional)
        
    Returns:
        Flask Response com o arquivo PDF para download
    """
    try:
        import pdfkit
        from jinja2 import Template
    except ImportError:
        raise ImportError("pdfkit e jinja2 são necessários para exportar para PDF. "
                        "Instale com 'pip install pdfkit jinja2' e instale wkhtmltopdf.")
    
    if not data:
        return None
    
    # Se não houver template, criar um padrão
    if not template_html:
        template_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Exportação de Dados</title>
            <style>
                body { font-family: Arial, sans-serif; }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .header { margin-bottom: 20px; }
                .footer { margin-top: 20px; font-size: 0.8em; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ title }}</h1>
                <p>Data de geração: {{ timestamp }}</p>
            </div>
            
            {% if is_table_data %}
            <table>
                <thead>
                    <tr>
                        {% for header in headers %}
                        <th>{{ header }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        {% for key in row %}
                        <td>{{ row[key] }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div>
                {% for key, value in data.items() %}
                <div>
                    <strong>{{ key }}:</strong> {{ value }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            <div class="footer">
                <p>Gerado por ProtestSystem</p>
            </div>
        </body>
        </html>
        """
    
    # Determinar se os dados são para tabela ou não
    is_table_data = isinstance(data, list)
    
    # Preparar contexto para o template
    context = {
        'title': 'Relatório de Dados',
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'data': data,
        'is_table_data': is_table_data,
        'headers': data[0].keys() if is_table_data and data else []
    }
    
    # Renderizar o template
    template = Template(template_html)
    html_content = template.render(**context)
    
    # Criar arquivo temporário para o PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        pdf_path = temp_file.name
    
    # Gerar PDF
    pdfkit.from_string(html_content, pdf_path)
    
    # Gerar nome de arquivo, se não fornecido
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_{timestamp}.pdf"
    
    # Retornar arquivo para download
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    ) 