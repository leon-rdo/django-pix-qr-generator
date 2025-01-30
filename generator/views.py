from django.views.generic import TemplateView
import base64
from io import BytesIO
import crcmod
import qrcode


class Payload():
    def __init__(self, nome, chavepix, valor, cidade, txtId, diretorio=''):
        self.nome = nome
        self.chavepix = chavepix
        self.valor = valor.replace(',', '.')
        self.cidade = cidade
        self.txtId = txtId
        self.diretorioQrCode = diretorio

        # Formata o valor para duas casas decimais
        self.valor_float = float(self.valor)
        self.valor_str = f"{self.valor_float:.2f}"
        self.valor_tam = len(self.valor_str)

        self.nome_tam = len(self.nome)
        self.chavepix_tam = len(self.chavepix)
        self.cidade_tam = len(self.cidade)
        self.txtId_tam = len(self.txtId)

        # Merchant Account em minúsculas
        self.merchantAccount_tam = f'0014br.gov.bcb.pix01{self.chavepix_tam:02}{self.chavepix}'
        self.transactionAmount_tam = f'{self.valor_tam:02}{self.valor_str}'

        self.addDataField_tam = f'05{self.txtId_tam:02}{self.txtId}'

        self.nome_tam = f'{self.nome_tam:02}'
        self.cidade_tam = f'{self.cidade_tam:02}'

        self.payloadFormat = '000201'
        self.merchantAccount = f'26{len(self.merchantAccount_tam):02}{self.merchantAccount_tam}'
        self.merchantCategCode = '52040000'
        self.transactionCurrency = '5303986'
        self.transactionAmount = f'54{self.transactionAmount_tam}'
        self.countryCode = '5802BR'
        self.merchantName = f'59{self.nome_tam}{self.nome}'
        self.merchantCity = f'60{self.cidade_tam}{self.cidade}'
        self.addDataField = f'62{len(self.addDataField_tam):02}{self.addDataField_tam}'
        self.crc16 = '6304'

    def gerarPayload(self):
        self.payload = f'{self.payloadFormat}{self.merchantAccount}{self.merchantCategCode}{self.transactionCurrency}{self.transactionAmount}{self.countryCode}{self.merchantName}{self.merchantCity}{self.addDataField}{self.crc16}'
        self.gerarCrc16(self.payload)

    def gerarCrc16(self, payload):
        # Usa o polinômio correto 0x11021 (CRC-16/CCITT-FALSE)
        crc16 = crcmod.mkCrcFun(poly=0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
        self.crc16Code = hex(crc16(payload.encode('utf-8')))
        self.crc16Code_formatado = self.crc16Code[2:].upper().zfill(4)
        self.payload_completa = f'{payload}{self.crc16Code_formatado}'

    def gerarQrCode(self, payload, diretorio):
        qr = qrcode.make(payload)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return qr_code_base64


class IndexView(TemplateView):
    template_name = 'generator/index.html'
    
    
class QrCodeView(TemplateView):
    template_name = 'generator/qrcode.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payload = Payload(
            self.request.GET.get('nome'),
            self.request.GET.get('chavepix'),
            self.request.GET.get('valor'),
            self.request.GET.get('cidade'),
            self.request.GET.get('txtId')
        )
        payload.gerarPayload()
        context['qr_code_base64'] = payload.gerarQrCode(payload.payload_completa, '')
        return context