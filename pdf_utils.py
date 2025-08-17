import logging
import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Line
from reportlab.platypus import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from utils import format_currency, get_weeks_in_month

# Đăng ký font để hỗ trợ tiếng Việt
font_name = 'DejaVuSans'  # Font mặc định hỗ trợ tiếng Việt
try:
    # Tìm font DejaVuSans
    font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
    if not os.path.exists(font_path):
        # Thử tìm trong môi trường PyInstaller
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'DejaVuSans.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        logging.info("Đã đăng ký font DejaVuSans thành công.")
    else:
        logging.warning("Không tìm thấy DejaVuSans.ttf, sử dụng Helvetica làm dự phòng.")
        font_name = 'Helvetica'
except Exception as e:
    logging.warning(f"Lỗi khi đăng ký DejaVuSans: {e}. Sử dụng Helvetica làm dự phòng.")
    font_name = 'Helvetica'

class CheckMark(Flowable):
    """Lớp tạo dấu tích tùy chỉnh để hiển thị trong PDF."""
    def __init__(self, width=8, height=8):
        Flowable.__init__(self)
        self.width = max(width, 6)
        self.height = max(height, 6)
    
    def draw(self):
        """Vẽ dấu tích trên canvas PDF."""
        self.canv.setStrokeColor(colors.black)
        self.canv.setLineWidth(1.5)
        self.canv.line(0, self.height/2, self.width/3, self.height/4)
        self.canv.line(self.width/3, self.height/4, self.width-2, self.height-2)

def export_to_pdf(username, month, year, data, learner_name, learner_id, sessions, fee):
    """
    Xuất bảng lương ra file PDF với định dạng lưới tuần, dấu tích cho ngày điểm danh, 
    tổng buổi và tổng phí.
    """
    try:
        # Kiểm tra dữ liệu đầu vào
        if not data:
            logging.error(f"Dữ liệu bảng lương rỗng cho username={username}, month={month}, year={year}, learner_id={learner_id}")
            return False, None
        for d in data:
            if not isinstance(d[0], str) or '/' not in d[0]:
                logging.error(f"Định dạng ngày không hợp lệ trong data: {d}")
                return False, None
        logging.info(f"Dữ liệu bảng lương hợp lệ: {data}, Tổng buổi: {sessions}, Tổng phí: {fee}")

        # Mở hộp thoại chọn nơi lưu file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        initial_file = f"Payroll_{username}_{month}_{year}_{timestamp}.pdf"
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Chọn nơi lưu file PDF",
            initialdir=os.path.expanduser("~/Desktop")
        )
        root.destroy()

        # Kiểm tra nếu người dùng hủy hộp thoại
        if not filename:
            logging.info("Xuất PDF bị hủy bởi người dùng.")
            return False, None

        # Kiểm tra quyền ghi vào thư mục
        directory = os.path.dirname(filename)
        if not os.access(directory, os.W_OK):
            logging.error(f"Không có quyền ghi vào thư mục: {directory}")
            return False, None

        if not learner_name:
            learner_name = "Bảng Lương"
            logging.warning("Tên người học rỗng, sử dụng tiêu đề mặc định.")

        # Tạo tài liệu PDF
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Thiết lập style cho tiêu đề và văn bản
        styles['Heading1'].fontName = font_name
        styles['Heading1'].fontSize = 16
        styles['Normal'].fontName = font_name
        styles['Normal'].fontSize = 9  # Giảm cỡ chữ để tránh xuống dòng
        styles.add(ParagraphStyle(name='Summary', fontName=font_name, fontSize=12, leading=14, spaceAfter=10))

        # Thêm tiêu đề
        elements.append(Paragraph(f"{learner_name} Tháng {month}/{year}", styles['Heading1']))
        elements.append(Spacer(1, 12))

        # Tạo bảng điểm danh
        table_data = [[""] + ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]]
        weeks = get_weeks_in_month(year, month)
        for i, week in enumerate(weeks, 1):
            row = [f"Tuần {i}"]
            for day in week:
                if day:
                    day_clean = day.strip()
                    checked = next((d[1] for d in data if d[0].strip() == day_clean), 0)
                    logging.debug(f"Ngày {day_clean} được điểm danh: {checked}")
                    if checked:
                        sub_table = Table([[Paragraph(day_clean, styles['Normal']), CheckMark()]], colWidths=[34, 8], rowHeights=[20])
                        sub_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Căn giữa cả ngày và dấu tick
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        row.append(sub_table)
                    else:
                        row.append(Paragraph(day_clean, styles['Normal']))
                else:
                    row.append("")
            table_data.append(row)

        # Tạo bảng
        table = Table(table_data, colWidths=[60] + [50] * 7, rowHeights=[30] * len(table_data))
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elements.append(table)

        # Thêm thông tin tóm tắt
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Tổng buổi: {sessions}", styles['Summary']))
        elements.append(Paragraph(f"Tổng phí: {format_currency(fee)}", styles['Summary']))

        # Tạo PDF
        doc.build(elements)
        logging.info(f"Đã xuất PDF thành công: {filename}")
        return True, filename
    except Exception as e:
        logging.error(f"Lỗi khi xuất PDF: {e}")
        return False, None