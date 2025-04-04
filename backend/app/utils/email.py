import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import current_app, render_template
from typing import List, Optional, Dict, Any


class EmailSender:
    """Classe para envio de e-mails"""
    
    def __init__(self):
        self.smtp_server = current_app.config.get('MAIL_SERVER')
        self.smtp_port = current_app.config.get('MAIL_PORT')
        self.smtp_username = current_app.config.get('MAIL_USERNAME')
        self.smtp_password = current_app.config.get('MAIL_PASSWORD')
        self.use_tls = current_app.config.get('MAIL_USE_TLS', False)
        self.use_ssl = current_app.config.get('MAIL_USE_SSL', False)
        self.default_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    
    def send_email(self, 
                  to: List[str], 
                  subject: str, 
                  body: str, 
                  html: Optional[str] = None, 
                  cc: Optional[List[str]] = None, 
                  bcc: Optional[List[str]] = None, 
                  attachments: Optional[List[Dict[str, Any]]] = None,
                  sender: Optional[str] = None) -> bool:
        """Envia um e-mail
        
        Args:
            to: Lista de destinatários
            subject: Assunto do e-mail
            body: Corpo do e-mail em texto plano
            html: Corpo do e-mail em HTML (opcional)
            cc: Lista de destinatários em cópia (opcional)
            bcc: Lista de destinatários em cópia oculta (opcional)
            attachments: Lista de anexos (opcional)
                Cada anexo deve ser um dicionário com as chaves:
                - filename: Nome do arquivo
                - content: Conteúdo do arquivo em bytes
                - content_type: Tipo de conteúdo (opcional, padrão: application/octet-stream)
            sender: Remetente (opcional, usa o padrão configurado se não informado)
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso, False caso contrário
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender or self.default_sender
            msg['To'] = ', '.join(to)
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Adiciona o corpo em texto plano
            part1 = MIMEText(body, 'plain')
            msg.attach(part1)
            
            # Adiciona o corpo em HTML, se fornecido
            if html:
                part2 = MIMEText(html, 'html')
                msg.attach(part2)
            
            # Adiciona anexos, se fornecidos
            if attachments:
                for attachment in attachments:
                    filename = attachment['filename']
                    content = attachment['content']
                    content_type = attachment.get('content_type', 'application/octet-stream')
                    
                    part = MIMEApplication(content)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    part.add_header('Content-Type', content_type)
                    msg.attach(part)
            
            # Configura o servidor SMTP
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                
                if self.use_tls:
                    server.starttls()
            
            # Faz login no servidor SMTP, se necessário
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            # Envia o e-mail
            recipients = to
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
                
            server.sendmail(msg['From'], recipients, msg.as_string())
            server.quit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar e-mail: {str(e)}")
            return False
    
    def send_template_email(self, 
                           to: List[str], 
                           subject: str, 
                           template_name: str, 
                           template_data: Dict[str, Any],
                           cc: Optional[List[str]] = None, 
                           bcc: Optional[List[str]] = None, 
                           attachments: Optional[List[Dict[str, Any]]] = None,
                           sender: Optional[str] = None) -> bool:
        """Envia um e-mail usando um template
        
        Args:
            to: Lista de destinatários
            subject: Assunto do e-mail
            template_name: Nome do template (sem extensão)
            template_data: Dados para renderizar o template
            cc: Lista de destinatários em cópia (opcional)
            bcc: Lista de destinatários em cópia oculta (opcional)
            attachments: Lista de anexos (opcional)
            sender: Remetente (opcional, usa o padrão configurado se não informado)
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso, False caso contrário
        """
        try:
            # Renderiza os templates
            text_body = render_template(f'email/{template_name}.txt', **template_data)
            html_body = render_template(f'email/{template_name}.html', **template_data)
            
            # Envia o e-mail
            return self.send_email(
                to=to,
                subject=subject,
                body=text_body,
                html=html_body,
                cc=cc,
                bcc=bcc,
                attachments=attachments,
                sender=sender
            )
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar e-mail com template: {str(e)}")
            return False


# Instância global para uso em toda a aplicação
email_sender = EmailSender()


def send_email(to, subject, body, html=None, cc=None, bcc=None, attachments=None, sender=None):
    """Função auxiliar para enviar e-mails"""
    return email_sender.send_email(
        to=to,
        subject=subject,
        body=body,
        html=html,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
        sender=sender
    )


def send_template_email(to, subject, template_name, template_data, cc=None, bcc=None, attachments=None, sender=None):
    """Função auxiliar para enviar e-mails usando templates"""
    return email_sender.send_template_email(
        to=to,
        subject=subject,
        template_name=template_name,
        template_data=template_data,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
        sender=sender
    )