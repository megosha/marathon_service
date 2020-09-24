from datetime import datetime, timedelta
from os import path
from fpdf import FPDF, HTMLMixin

from django.conf import settings


media_dir = settings.MEDIA_ROOT

class CustomPDF(FPDF):
    pass


def create_pdf(payment):
    # if not payment:
    #     payment = Payment.objects.filter().first()
    pdf_path = path.join(media_dir, 'invoice', f'{payment.uuid}.pdf')
    pdf = CustomPDF()
    # Создаем особое значение {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    # Устанавливаем лого
    # self.image('snakehead.jpg', 10, 8, 33)
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    # self.set_font('Arial', 'B', 15)
    # Добавляем адрес
    offset = pdf.w / 2.5 + 55
    pdf.cell(offset)
    pdf.cell(0, 5, 'Иванов Иван Ианович', ln=1)
    pdf.cell(offset)
    pdf.cell(0, 5, '9132131232', ln=1)
    pdf.cell(offset)
    pdf.cell(0, 5, 'email@email.com', ln=1)
    # Line break Разрыв линии
    pdf.ln(20)
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(200, 10, txt=f"Квитанция", ln=1, align="C")
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(10)
    pdf.cell(pdf.w / 2.5, 5, 'Детали квитанции:')
    pdf.cell(45)
    pdf.cell(0, 5, 'Покупатель:', ln=1)
    pdf.cell(10)
    pdf.cell(pdf.w / 2.5, 5, f'Дата оплаты: {payment.date_pay.strftime("%d.%m.%Y")}')
    pdf.cell(45)
    pdf.cell(0, 5, f'{payment.account.user.last_name} {payment.account.user.first_name}', ln=1)
    pdf.cell(10)
    pdf.cell(pdf.w / 2.5, 5, f'Номер заказа: {payment.uuid}')
    pdf.cell(45)
    pdf.cell(0, 5, f'{payment.account.phone}', ln=1)
    pdf.cell(10)
    pdf.cell(pdf.w / 2.5, 5, '')
    pdf.cell(45)
    pdf.cell(0, 5, f'{payment.account.user.email}', ln=1)
    # pdf.ln(5)
    pdf.set_font('DejaVu', '', 8)
    spacing = 1
    data = [['Товар/услуга', 'Описание', 'Стоимость', 'Количество', 'Сумма'],
            [f'Марафон "{payment.marathon.title}", '
             f'Персональная двухмесячная подписка на срок с {payment.date_pay.strftime("%d.%m.%Y")} по'
             f' {(payment.date_pay + timedelta(days=62)).strftime("%d.%m.%Y")}',
             f'{payment.amount}.00', '1', f'{payment.amount}.00 Руб']
            ]
    col_widths = [50, 55, 25, 20, 30]
    # col_width = pdf.w / 5.5
    row_height = pdf.font_size * 2
    top = pdf.y
    for i, row in enumerate(data):
        top += row_height
        for j, item in enumerate(row):
            # pdf.cell(col_width, row_height * spacing, txt=item, border=1, align="L")
            pdf.y = top
            # offset = pdf.x + col_width
            # pdf.multi_cell(col_width, row_height * spacing, item, 1, 0)
            offset = pdf.x + col_widths[j]
            if i == 1 and j > 1: row_height = pdf.font_size * 4
            pdf.multi_cell(col_widths[j], row_height * spacing, item, 1, 0)
            pdf.x = offset
        pdf.ln(row_height * spacing)
    # pdf.ln(5)
    pdf.cell(200, 5, txt=f"Итого: {payment.amount} руб. 00 коп.", ln=1, align="L")
    # pdf.cell(200, 5, txt="Сумма прописью: Один рубль ноль копеек", ln=1, align="L")  # TODO
    pdf.output(pdf_path)
    return pdf_path