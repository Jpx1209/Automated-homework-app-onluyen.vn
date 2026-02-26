from google import genai
import os
import re
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def choose_working_model():

    try:
        models = client.models.list()
        for model in models:
            if 'generateContent' in str(model.supported_actions):
                if 'flash' in model.name:
                    return model.name
        return "models/gemini-1.5-flash"
    except Exception as e:
        print(f"⚠️ [Hệ thống] Không liệt kê được model, dùng mặc định: {e}")
        return "models/gemini-1.5-flash"

model_name = choose_working_model()
print(f"✅ [AI] Sử dụng model: {model_name}")

def solve_question(question_text, options=None, is_fill_blank=False):
    """

    """
    if not question_text or question_text.strip() == "" or "N/A" in question_text:
        if not re.search(r'[a-zA-Z]{2,}', str(question_text)):
            print("❓ [AI] Cảnh báo: Dữ liệu câu hỏi quá ngắn hoặc trống.")
            return None

    clean_q = re.sub(r'#\d+', '', question_text).strip()

    if is_fill_blank:
        prompt = f"""
        TASK: Fill in the blank for this English sentence.
        CONTEXT: {clean_q}
        RULES: 
        - Return ONLY the missing word or phrase.
        - Do not rewrite the sentence. 
        - Do not explain.
        """
        print(f"🧠 [AI] Đang giải dạng ĐIỀN Ô...")
    else:
        prompt = f"""
        TASK: Solve this multiple-choice question.
        QUESTION: {clean_q}
        CHOICES:
        A: {options.get('A', 'N/A')}
        B: {options.get('B', 'N/A')}
        C: {options.get('C', 'N/A')}
        D: {options.get('D', 'N/A')}
        RULES: Return ONLY the letter A, B, C, or D.
        """
        print(f"🧠 [AI] Đang giải dạng KHOANH (A,B,C,D)...")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        res_text = response.text.strip()

        if is_fill_blank:
            ans = res_text.replace('"', '').replace('.', '').strip()
            print(f"🤖 [AI Kết quả] Từ cần điền: '{ans}'")
            return ans
        else:
            match = re.search(r"\b[A-D]\b", res_text.upper())
            if match:
                ans = match.group(0)
                print(f"🤖 [AI Kết quả] Đáp án chọn: {ans}")
                return ans
            else:
                print(f"⚠️ [AI] Không tìm thấy đáp án trong: {res_text}")
                return None
    except Exception as e:
        if "429" in str(e):
            print("❌ [AI Lỗi] Quá tải API (Rate limit).")
            return "RETRY"
        print(f"❌ [AI Lỗi] {e}")
    return None

def solve_true_false(question_text):

    prompt = f"""
    Cho câu hỏi sau (có thể kèm các phát biểu a, b, c, d):
    {question_text}

    Hãy xác định các phát biểu a, b, c, d là đúng hay sai.
    Trả về kết quả theo định dạng:
    a: Đúng
    b: Sai
    c: Đúng
    d: Sai
    (Chỉ trả về các dòng này, không thêm giải thích hay ký tự khác)
    """
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        res_text = response.text.strip()
        lines = res_text.split('\n')
        results = {}
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip().lower()
                val = val.strip().lower()
                if key in ['a', 'b', 'c', 'd'] and val in ['đúng', 'sai']:
                    results[key] = 'Đúng' if val == 'đúng' else 'Sai'
        if len(results) == 4:
            print(f"🤖 [AI Kết quả] {results}")
            return results
        else:
            print(f"⚠️ [AI] Kết quả không đầy đủ: {res_text}")
            return None
    except Exception as e:
        if "429" in str(e):
            print("❌ [AI Lỗi] Quá tải API (Rate limit).")
            return "RETRY"
        print(f"❌ [AI Lỗi] {e}")
        return None