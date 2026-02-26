
# 📚 Automated Homework Tool – onluyen.vn

**by jpx1209**

Tool hỗ trợ tự động đăng nhập và làm bài trên **onluyen.vn** bằng AI.

---

## 🚀 Hướng dẫn sử dụng

### 🔹 Bước 1: Tải project từ GitHub

```bash
git clone https://github.com/Jpx1209/Automated-homework-app-onluyen.vn.git
cd Automated-homework-app-onluyen.vn
```

Hoặc tải file `.zip` rồi giải nén.

---

### 🔹 Bước 2: Cài đặt Python & thư viện

📌 Yêu cầu: **Python 3.9+**

Cài các thư viện cần thiết:

```bash
pip install playwright python-dotenv google-generativeai
playwright install
```

Nếu project có `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 🔹 Bước 3: Các thư viện được sử dụng

Tool sử dụng các thư viện sau:

```python
import sys
import io
from playwright.sync_api import sync_playwright
from ai_engine import solve_question, solve_true_false
import os
import time
import re
import json
from dotenv import load_dotenv
from google import genai
import warnings
```

---

### 🔹 Bước 4: Tạo file `.env`

Tạo file `.env` trong thư mục gốc project và điền thông tin:

```env
APP_USERNAME=
APP_PASSWORD=
GEMINI_API_KEY=
PRACTICE_URL=
```

📌 Giải thích:

| Biến             | Mô tả                 |
| ---------------- | --------------------- |
| `APP_USERNAME`   | Tài khoản onluyen.vn  |
| `APP_PASSWORD`   | Mật khẩu onluyen.vn   |
| `GEMINI_API_KEY` | API key Google Gemini |
| `PRACTICE_URL`   | Link bài luyện tập    |

---

### 🔹 Bước 5: Chạy tool

```bash
py main.py
```

Hoặc:

```bash
python main.py
```

---

## ⚠️ Lưu ý


* 📖 Chỉ sử dụng cho mục đích học tập và nghiên cứu , vọc vạch ,...


---

## 🛠️ Tính năng

* ✅ Tự động đăng nhập
* ✅ Tự động làm bài trắc nghiệm
* ✅ Hỗ trợ câu hỏi đúng/sai
* ✅ Hỗ trợ câu hỏi điền .,, 
* ✅ Sử dụng AI Gemini để giải bài
* Discord- better_ars (Ars)
---
## 🎥 Video Demo

<a href="https://youtu.be/cY6AibeE7R8">
  <img src="https://img.youtube.com/vi/cY6AibeE7R8/maxresdefault.jpg" alt="Video Demo" width="600">
</a>


Nếu bạn muốn cải thiện tool, hãy tạo Pull Request hoặc Issue trên GitHub.

---

## 📜 License

MIT License
