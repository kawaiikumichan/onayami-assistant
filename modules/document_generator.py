from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os
import tempfile
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

def create_pdf_report(messages, facts=None):
    """
    Generates a simple PDF report from the chat history and extracted facts.
    """
    try:
        # Create a temporary file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "consultation_sheet.pdf")
        
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # Register a Japanese font (HeiseiKakuGo-W5 is a standard CID font)
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
        c.setFont("HeiseiKakuGo-W5", 14)
        
        y_position = height - 30 * mm
        c.drawString(20 * mm, y_position, "法律相談事前整理シート (Legal Prep)")
        
        c.setFont("HeiseiKakuGo-W5", 10)
        y_position -= 10 * mm
        c.drawString(20 * mm, y_position, "※本シートはAIとの対話ログであり、法的効力を持ちません。弁護士相談の参考資料としてお使いください。")
        y_position -= 15 * mm

        # --- Structured Facts Section ---
        if facts:
            c.setFont("HeiseiKakuGo-W5", 12)
            c.drawString(20 * mm, y_position, "■ 事実関係の整理")
            y_position -= 8 * mm
            
            c.setFont("HeiseiKakuGo-W5", 10)
            
            fact_labels = {
                "main_issue": "相談内容概要",
                "timeline": "時系列",
                "parties": "関係者",
                "evidence": "証拠",
                "user_desire": "希望する解決",
                "missing_info": "不足している情報"
            }
            
            for key, label in fact_labels.items():
                value = facts.get(key, "不明")
                if isinstance(value, list):
                    value = ", ".join(value) if value else "なし"
                
                # Check page break
                if y_position < 30 * mm:
                    c.showPage()
                    y_position = height - 30 * mm
                    c.setFont("HeiseiKakuGo-W5", 10)

                # Draw Label
                c.drawString(20 * mm, y_position, f"【{label}】")
                y_position -= 5 * mm
                
                # Draw Content (Simple wrap)
                text = str(value)
                max_chars = 45
                lines = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
                
                for line in lines:
                    c.drawString(25 * mm, y_position, line)
                    y_position -= 5 * mm
                
                y_position -= 2 * mm # Extra space between items

            y_position -= 10 * mm

        # --- Chat History Section ---
        if y_position < 40 * mm:
            c.showPage()
            y_position = height - 30 * mm
        
        c.setFont("HeiseiKakuGo-W5", 12)
        c.drawString(20 * mm, y_position, "■ 対話ログ")
        y_position -= 8 * mm

        c.setFont("HeiseiKakuGo-W5", 10)
        
        for msg in messages:
            role = "ユーザー" if msg["role"] == "user" else "AI助手"
            content = msg["content"]
            
            # Simple word wrap logic
            prefix = f"[{role}]: "
            text = prefix + content
            
            max_chars = 45
            lines = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
            
            for line in lines:
                if y_position < 20 * mm:
                    c.showPage()
                    y_position = height - 20 * mm
                    c.setFont("HeiseiKakuGo-W5", 10)
                
                c.drawString(20 * mm, y_position, line)
                y_position -= 6 * mm
            
            y_position -= 4 * mm # Extra space between messages

        c.save()
        return file_path
    
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return None
