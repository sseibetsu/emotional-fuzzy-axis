from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import os
from datetime import datetime


class PDFReportGenerator:
    def __init__(self, filename="emotion_report.pdf"):
        self.filename = filename
        self.width, self.height = A4
        self.register_font()

    def register_font(self):
        try:
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arial', font_path))
                self.font_name = 'Arial'
            else:
                self.font_name = 'Helvetica'
        except:
            self.font_name = 'Helvetica'

    def generate(self, emotions_history):
        c = canvas.Canvas(self.filename, pagesize=A4)

        # 1. ЗАГОЛОВОК
        c.setFont(self.font_name, 24)
        c.drawString(50, 800, "Отчет психоэмоционального анализа")

        c.setFont(self.font_name, 12)
        c.setFillColor(colors.gray)
        date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        c.drawString(50, 780, f"Дата сессии: {date_str}")
        c.drawString(50, 765, "Сгенерировано AI-Терапевтом (Diploma Project)")

        # 2. СТАТИСТИКА
        c.setFillColor(colors.black)
        c.setFont(self.font_name, 16)
        c.drawString(50, 720, "Сводка сессии:")

        if not emotions_history:
            emotions_history = ["neutral"]

        most_common = max(set(emotions_history), key=emotions_history.count)
        total_msgs = len(emotions_history)

        c.setFont(self.font_name, 12)
        c.drawString(
            70, 690, f"• Всего сообщений проанализировано: {total_msgs}")
        c.drawString(70, 670, f"• Доминирующая эмоция: {most_common.upper()}")

        # 3. ВИЗУАЛИЗАЦИЯ (ГРАФИК)
        c.setFont(self.font_name, 16)
        c.drawString(50, 620, "Динамика эмоционального тона:")

        origin_x, origin_y = 70, 450
        c.line(origin_x, origin_y, origin_x + 400, origin_y)  # Ось X
        c.line(origin_x, origin_y, origin_x, origin_y + 100)  # Ось Y

        c.setFont(self.font_name, 8)
        c.drawString(origin_x - 30, origin_y + 90, "Позитив")
        c.drawString(origin_x - 30, origin_y + 10, "Негатив")

        points = []
        for i, emo in enumerate(emotions_history[-10:]):  # Берем последние 10
            y_val = 50  # neutral
            if emo in ['joy', 'love', 'gratitude', 'admiration', 'excitement']:
                y_val = 90
            elif emo in ['anger', 'sadness', 'fear', 'disappointment', 'grief']:
                y_val = 20

            x_pos = origin_x + (i * 40)
            y_pos = origin_y + y_val
            points.append((x_pos, y_pos))

            c.setFillColor(colors.blue)
            c.circle(x_pos, y_pos, 3, fill=1)

            c.setFillColor(colors.gray)
            c.drawString(x_pos - 10, y_pos - 15, emo[:3])  # Первые 3 буквы

        c.setStrokeColor(colors.blue)
        if len(points) > 1:
            p = c.beginPath()
            p.moveTo(points[0][0], points[0][1])
            for point in points[1:]:
                p.lineTo(point[0], point[1])
            c.drawPath(p)

        c.setFont(self.font_name, 10)
        c.setFillColor(colors.gray)
        c.drawString(
            50, 50, "Примечание: Данный отчет сгенерирован автоматически с использованием RAG & Fuzzy Logic.")

        c.save()
        return self.filename
