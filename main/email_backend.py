"""
Кастомный email backend для решения проблем с SSL сертификатами
"""
import smtplib
from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend
from django.conf import settings

class CustomEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssl_context = getattr(settings, 'EMAIL_SSL_CONTEXT', None)
    
    def open(self):
        if self.connection:
            return False
        
        try:
            if self.use_ssl:
                # SSL соединение
                if self.ssl_context:
                    self.connection = smtplib.SMTP_SSL(self.host, self.port, context=self.ssl_context)
                else:
                    self.connection = smtplib.SMTP_SSL(self.host, self.port)
            else:
                # Обычное соединение с возможностью TLS
                self.connection = smtplib.SMTP(self.host, self.port)
                if self.use_tls:
                    if self.ssl_context:
                        self.connection.starttls(context=self.ssl_context)
                    else:
                        self.connection.starttls()
            
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception as e:
            if not self.fail_silently:
                raise e
            return False
