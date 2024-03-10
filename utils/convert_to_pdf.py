import io
import PyPDF2


def convert_buffer_to_pdf(buffer, output_file_path):
    # Создаем объект PDF
    pdf_writer = PyPDF2.PdfWriter()
    pdf_reader = PyPDF2.PdfReader(buffer)
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_writer.add_page(page)

    # Записываем данные в новый PDF файл
    with open(output_file_path + '.pdf', 'wb') as output_file:
        pdf_writer.write(output_file)

