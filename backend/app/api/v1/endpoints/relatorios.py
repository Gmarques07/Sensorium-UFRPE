from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Tuple
from datetime import datetime, date
from collections import defaultdict
from backend.app.api.deps import get_db, get_current_user
from backend.app.models.usuario import Usuario
from backend.app.models.local import Local, PhNivel, NivelAgua
# from app.utils.email import send_relatorio_por_email
from backend.app.utils.email_yagmail import send_relatorio_por_email_yagmail as send_relatorio_por_email
from backend.app.core.config import settings
import csv
import io
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

router = APIRouter()

# Cores da identidade visual do Sensorium
PRIMARY_BLUE = colors.Color(0, 102/255, 204/255)  # #0066cc
SECONDARY_BLUE = colors.Color(0, 51/255, 102/255)  # #003366
ACCENT_GREEN = colors.Color(0, 230/255, 118/255)  # #00E676
LIGHT_BG = colors.Color(245/255, 249/255, 255/255)  # #f5f9ff
CARD_BG = colors.white
BORDER_RADIUS = 15

def calcular_estatisticas_diarias_ph(dados_ph: List[PhNivel]) -> Dict[str, Dict[str, float]]:
    """
    Calcula média, máximo e mínimo diários para dados de pH.
    """
    estatisticas = defaultdict(list)
    
    # Agrupar dados por data
    for item in dados_ph:
        data_str = item.data.strftime("%Y-%m-%d")
        estatisticas[data_str].append(item.ph)
    
    # Calcular estatísticas para cada dia
    resultado = {}
    for data, valores in estatisticas.items():
        resultado[data] = {
            "media": round(sum(valores) / len(valores), 2),
            "maximo": max(valores),
            "minimo": min(valores)
        }
    
    return resultado

def calcular_estatisticas_diarias_nivel(dados_nivel: List[NivelAgua]) -> Dict[str, Dict[str, float]]:
    """
    Calcula média, máximo e mínimo diários para dados de nível.
    """
    estatisticas = defaultdict(list)
    
    # Agrupar dados por data
    for item in dados_nivel:
        data_str = item.data.strftime("%Y-%m-%d")
        estatisticas[data_str].append(item.boia)
    
    # Calcular estatísticas para cada dia
    resultado = {}
    for data, valores in estatisticas.items():
        resultado[data] = {
            "media": round(sum(valores) / len(valores), 1),
            "maximo": max(valores),
            "minimo": min(valores)
        }
    
    return resultado

def obter_dados_relatorio(db: Session, inicio: date, fim: date, dispositivo: Optional[str] = None):
    """
    Função auxiliar para obter os dados do relatório com base nos filtros.
    """
    # Validar datas
    if inicio > fim:
        raise HTTPException(status_code=400, detail="A data inicial deve ser menor ou igual à data final.")
    
    # Converter datas para datetime
    inicio_dt = datetime.combine(inicio, datetime.min.time())
    fim_dt = datetime.combine(fim, datetime.max.time())
    
    # Query base para PhNivel
    query_ph = db.query(PhNivel).join(Local).filter(
        PhNivel.data >= inicio_dt,
        PhNivel.data <= fim_dt
    )
    
    # Query base para NivelAgua
    query_nivel = db.query(NivelAgua).join(Local).filter(
        NivelAgua.data >= inicio_dt,
        NivelAgua.data <= fim_dt
    )
    
    # Filtrar por dispositivo, se especificado
    if dispositivo:
        local = db.query(Local).filter(Local.nome == dispositivo).first()
        if not local:
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
        query_ph = query_ph.filter(PhNivel.local_id == local.id)
        query_nivel = query_nivel.filter(NivelAgua.local_id == local.id)
    
    # Executar queries
    dados_ph = query_ph.order_by(PhNivel.data).all()
    dados_nivel = query_nivel.order_by(NivelAgua.data).all()
    
    return dados_ph, dados_nivel

def gerar_relatorio_pdf(inicio: date, fim: date, dispositivo: Optional[str], dados_ph: List[PhNivel], dados_nivel: List[NivelAgua]):
    """
    Gera o conteúdo do relatório PDF.
    """
    # Calcular estatísticas diárias
    estatisticas_ph = calcular_estatisticas_diarias_ph(dados_ph)
    estatisticas_nivel = calcular_estatisticas_diarias_nivel(dados_nivel)
    
    # Criar o conteúdo PDF em memória
    buffer = io.BytesIO()
    # Usar A4 para melhor visualização de tabelas
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=PRIMARY_BLUE,
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        spaceBefore=25,
        textColor=SECONDARY_BLUE,
        fontName='Helvetica-Bold'
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        textColor=colors.black
    )
    small_style = ParagraphStyle(
        'Small',
        parent=normal_style,
        fontSize=9,
        spaceAfter=6,
        textColor=colors.grey
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    # Caminho para a logo
    # O PDF vai ser gerado no backend, então precisamos do caminho absoluto
    # Vamos assumir que o diretório static está no mesmo nível do diretório backend
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logo_path = os.path.join(base_dir, "static", "img", "logo.svg")
    
    # Adicionar logo, se existir
    if os.path.exists(logo_path):
        try:
            # Adicionar a logo com tamanho fixo
            logo = Image(logo_path, width=60, height=60)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 10))
        except:
            # Se houver erro ao carregar a logo, continuar sem ela
            pass
    
    # Cabeçalho com identidade visual
    # Título principal
    elements.append(Paragraph("Sistema Sensorium UFRPE", title_style))
    
    # Subtítulo
    periodo = f"Relatório de Monitoramento - {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(periodo, ParagraphStyle(
        'Subtitle',
        parent=normal_style,
        fontSize=12,
        alignment=TA_CENTER,
        textColor=SECONDARY_BLUE
    )))
    
    # Dispositivo, se especificado
    if dispositivo:
        elements.append(Paragraph(f"Dispositivo: {dispositivo}", ParagraphStyle(
            'Device',
            parent=normal_style,
            fontSize=11,
            alignment=TA_CENTER,
            textColor=PRIMARY_BLUE
        )))
    
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", small_style))
    elements.append(Spacer(1, 20))
    
    # Se não houver dados
    if not dados_ph and not dados_nivel:
        elements.append(Paragraph("Nenhum dado encontrado para o período especificado.", normal_style))
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    # Seção de Estatísticas Diárias de pH
    if estatisticas_ph:
        elements.append(Paragraph("Estatísticas Diárias de pH", heading_style))
        ph_stats_data = [["Data", "Média", "Máximo", "Mínimo"]]
        
        # Ordenar datas
        datas_ordenadas = sorted(estatisticas_ph.keys())
        for data in datas_ordenadas:
            stats = estatisticas_ph[data]
            ph_stats_data.append([
                datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y"),
                str(stats["media"]),
                str(stats["maximo"]),
                str(stats["minimo"])
            ])
        
        ph_stats_table = Table(ph_stats_data, colWidths=[100, 80, 80, 80])
        ph_stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BG),
            ('GRID', (0, 0), (-1, -1), 1, PRIMARY_BLUE),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ]))
        elements.append(ph_stats_table)
        elements.append(Spacer(1, 20))
    
    # Seção de Estatísticas Diárias de Nível
    if estatisticas_nivel:
        elements.append(Paragraph("Estatísticas Diárias de Nível", heading_style))
        nivel_stats_data = [["Data", "Média (%)", "Máximo (%)", "Mínimo (%)"]]
        
        # Ordenar datas
        datas_ordenadas = sorted(estatisticas_nivel.keys())
        for data in datas_ordenadas:
            stats = estatisticas_nivel[data]
            nivel_stats_data.append([
                datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y"),
                f"{stats['media']:.1f}",
                str(stats["maximo"]),
                str(stats["minimo"])
            ])
        
        nivel_stats_table = Table(nivel_stats_data, colWidths=[100, 80, 80, 80])
        nivel_stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BG),
            ('GRID', (0, 0), (-1, -1), 1, PRIMARY_BLUE),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ]))
        elements.append(nivel_stats_table)
        elements.append(Spacer(1, 20))
        elements.append(PageBreak())  # Nova página para os dados detalhados
    
    # Dados detalhados de pH
    if dados_ph:
        elements.append(Paragraph("Dados Detalhados de pH", heading_style))
        ph_data = [["Data/Hora", "Dispositivo", "pH"]]
        for item in dados_ph:
            ph_data.append([
                item.data.strftime("%d/%m/%Y %H:%M:%S"),
                item.local.nome,
                str(item.ph)
            ])
        
        ph_table = Table(ph_data, colWidths=[120, 150, 80])
        ph_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BG),
            ('GRID', (0, 0), (-1, -1), 1, PRIMARY_BLUE),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ]))
        elements.append(ph_table)
        elements.append(Spacer(1, 20))
    
    # Dados detalhados de Nível
    if dados_nivel:
        elements.append(Paragraph("Dados Detalhados de Nível", heading_style))
        nivel_data = [["Data/Hora", "Dispositivo", "Status", "Boia (%)"]]
        for item in dados_nivel:
            nivel_data.append([
                item.data.strftime("%d/%m/%Y %H:%M:%S"),
                item.local.nome,
                item.status,
                str(item.boia) if item.boia is not None else "N/A"
            ])
        
        nivel_table = Table(nivel_data, colWidths=[120, 150, 80, 80])
        nivel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BG),
            ('GRID', (0, 0), (-1, -1), 1, PRIMARY_BLUE),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ]))
        elements.append(nivel_table)
    
    # Rodapé
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Relatório gerado pelo Sistema Sensorium UFRPE", footer_style))
    elements.append(Paragraph("www.sensorium.ufrpe.br", ParagraphStyle(
        'Website',
        parent=footer_style,
        textColor=PRIMARY_BLUE,
        underline=True
    )))
    
    # Construir o PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer.getvalue()

@router.get("/exportar.csv")
def exportar_relatorio_csv(
    inicio: date = Query(..., description="Data inicial no formato YYYY-MM-DD"),
    fim: date = Query(..., description="Data final no formato YYYY-MM-DD"),
    dispositivo: Optional[str] = Query(None, description="Nome do dispositivo (opcional)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Exporta os dados do relatório no formato CSV.
    """
    dados_ph, dados_nivel = obter_dados_relatorio(db, inicio, fim, dispositivo)
    
    # Criar o conteúdo CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escrever cabeçalhos
    writer.writerow(["Tipo", "Dispositivo", "Data", "Valor", "Status/Boia"])
    
    # Escrever dados de pH
    for item in dados_ph:
        writer.writerow([
            "pH",
            item.local.nome,
            item.data.strftime("%Y-%m-%d %H:%M:%S"),
            item.ph,
            ""
        ])
    
    # Escrever dados de Nível
    for item in dados_nivel:
        writer.writerow([
            "Nível",
            item.local.nome,
            item.data.strftime("%Y-%m-%d %H:%M:%S"),
            "",
            f"{item.status} ({item.boia}%)" if item.boia is not None else item.status
        ])
    
    # Obter o conteúdo CSV
    csv_content = output.getvalue()
    output.close()
    
    # Criar a resposta com o conteúdo CSV
    headers = {
        'Content-Disposition': f'attachment; filename="relatorio_{inicio.strftime("%Y%m%d")}_{fim.strftime("%Y%m%d")}.csv"'
    }
    return Response(content=csv_content, media_type="text/csv", headers=headers)


@router.get("/exportar.pdf")
def exportar_relatorio_pdf_endpoint(
    inicio: date = Query(..., description="Data inicial no formato YYYY-MM-DD"),
    fim: date = Query(..., description="Data final no formato YYYY-MM-DD"),
    dispositivo: Optional[str] = Query(None, description="Nome do dispositivo (opcional)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Exporta os dados do relatório no formato PDF.
    """
    dados_ph, dados_nivel = obter_dados_relatorio(db, inicio, fim, dispositivo)
    
    # Gerar o PDF
    pdf_content = gerar_relatorio_pdf(inicio, fim, dispositivo, dados_ph, dados_nivel)
    
    # Criar a resposta com o conteúdo PDF
    headers = {
        'Content-Disposition': f'attachment; filename="relatorio_{inicio.strftime("%Y%m%d")}_{fim.strftime("%Y%m%d")}.pdf"'
    }
    return Response(content=pdf_content, media_type="application/pdf", headers=headers)


@router.post("/enviar-por-email")
def enviar_relatorio_por_email(
    inicio: date = Query(..., description="Data inicial no formato YYYY-MM-DD"),
    fim: date = Query(..., description="Data final no formato YYYY-MM-DD"),
    dispositivo: Optional[str] = Query(None, description="Nome do dispositivo (opcional)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera o relatório e envia por e-mail para o usuário.
    """
    # Verificar se o envio de e-mails está configurado
    if not settings.emails_enabled:
        raise HTTPException(
            status_code=500,
            detail="Serviço de e-mail não está configurado. Contate o administrador do sistema."
        )
    
    # Verificar se o usuário tem e-mail cadastrado
    if not current_user.email:
        raise HTTPException(
            status_code=400,
            detail="Usuário não possui e-mail cadastrado."
        )
    
    # Obter dados do relatório
    dados_ph, dados_nivel = obter_dados_relatorio(db, inicio, fim, dispositivo)
    
    # Gerar o PDF
    pdf_content = gerar_relatorio_pdf(inicio, fim, dispositivo, dados_ph, dados_nivel)
    
    # Enviar e-mail
    sucesso = send_relatorio_por_email(
        email_to=current_user.email,
        pdf_data=pdf_content,
        inicio=inicio.strftime("%d/%m/%Y"),
        fim=fim.strftime("%d/%m/%Y"),
        dispositivo=dispositivo
    )
    
    if sucesso:
        return {"message": f"Relatório enviado com sucesso para {current_user.email}"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Erro ao enviar o relatório por e-mail. Tente novamente mais tarde."
        )