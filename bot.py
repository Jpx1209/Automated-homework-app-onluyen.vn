from playwright.sync_api import sync_playwright
from ai_engine import solve_question, solve_true_false
import os
import time
import re
import json
from dotenv import load_dotenv

load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")
PRACTICE_URL = os.getenv("PRACTICE_URL")

if not PRACTICE_URL:
    print("❌ [Hệ thống] Lỗi: Chưa có PRACTICE_URL trong file .env")
    exit()

def log_question_to_file(filename, data):
    existing_data = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except:
                existing_data = []
    existing_data.append(data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

def get_data_by_scraping(page):
    try:
        body_text = page.evaluate("() => document.body.innerText")
        id_match = re.search(r"#(\d+)", body_text)
        q_id = id_match.group(1) if id_match else "unknown"

        lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        options = {"A": "N/A", "B": "N/A", "C": "N/A", "D": "N/A"}

        for i, line in enumerate(lines):
            if line == "A" or line.startswith("A "):
                options["A"] = lines[i+1] if i+1 < len(lines) else "N/A"
            elif line == "B" or line.startswith("B "):
                options["B"] = lines[i+1] if i+1 < len(lines) else "N/A"
            elif line == "C" or line.startswith("C "):
                options["C"] = lines[i+1] if i+1 < len(lines) else "N/A"
            elif line == "D" or line.startswith("D "):
                options["D"] = lines[i+1] if i+1 < len(lines) else "N/A"

        question = page.evaluate("""() => {
            const qEl = document.querySelector('.question-content-container') || 
                        document.querySelector('.question-text') ||
                        document.querySelector('.content-question');
            return qEl ? qEl.innerText.trim() : ""; 
        }""")

        if not question:
            q_search = re.search(r"#\d+.*?\n(.*?)(?=\n\s*A\s*\n)", body_text, re.DOTALL)
            if q_search:
                question = q_search.group(1).strip()
            else:
                question = body_text.split(f"#{q_id}")[-1][:300].strip()

        return q_id, question, options
    except Exception as e:
        print(f"⚠️ [Lỗi quét] {e}")
        return "unknown", "N/A", {"A": "N/A", "B": "N/A", "C": "N/A", "D": "N/A"}

def click_true_false(page, results):

    page.screenshot(path="debug_truefalse.png")
    print("📸 Đã chụp debug_truefalse.png để kiểm tra giao diện")


    labels = page.locator("label:has-text('Đúng'), label:has-text('Sai')").all()
    print(f"🔍 Tìm thấy {len(labels)} label Đúng/Sai")

    if len(labels) == 8:

        label_texts = [label.text_content().strip() for label in labels]
        print(f"📝 Text các label: {label_texts}")


        for idx, (key, value) in enumerate(results.items()):
            start = idx * 2
            if start + 1 >= len(labels):
                break

            label1 = labels[start]
            label2 = labels[start+1]
            text1 = label1.text_content().strip()
            text2 = label2.text_content().strip()

            if text1 == "Đúng" and text2 == "Sai":

                target = label1 if value == "Đúng" else label2
            elif text1 == "Sai" and text2 == "Đúng":
                target = label2 if value == "Đúng" else label1
            else:

                if text1 == value:
                    target = label1
                elif text2 == value:
                    target = label2
                else:
                    print(f"   ⚠️ Không tìm thấy label {value} cho {key}")
                    continue
            try:
                target.click(force=True)
                print(f"   ✅ Đã chọn {key} {value} (cách 1 - label cặp)")
            except:
                print(f"   ❌ Không click được label cho {key}")
    elif len(labels) == 4:

        for idx, (key, value) in enumerate(results.items()):
            if idx >= len(labels):
                break
            label = labels[idx]
            label_text = label.text_content().strip()
            if label_text == value:
                try:
                    label.click(force=True)
                    print(f"   ✅ Đã chọn {key} {value} (cách 1 - label đơn)")
                except:
                    pass
            else:
                print(f"   ⚠️ Label {key} có text '{label_text}' không khớp {value}")
    else:

        print("⚠️ Không tìm thấy đủ label, chuyển sang tìm button")


        buttons = page.locator("button:has-text('Đúng'), button:has-text('Sai')").all()
        print(f"🔍 Tìm thấy {len(buttons)} button Đúng/Sai")
        if len(buttons) == 8:

            for idx, (key, value) in enumerate(results.items()):
                start = idx * 2
                if start + 1 >= len(buttons):
                    break
                btn1 = buttons[start]
                btn2 = buttons[start+1]
                text1 = btn1.text_content().strip()
                text2 = btn2.text_content().strip()
                if text1 == "Đúng" and text2 == "Sai":
                    target = btn1 if value == "Đúng" else btn2
                elif text1 == "Sai" and text2 == "Đúng":
                    target = btn2 if value == "Đúng" else btn1
                else:
                    if text1 == value:
                        target = btn1
                    elif text2 == value:
                        target = btn2
                    else:
                        continue
                try:
                    target.click(force=True)
                    print(f"   ✅ Đã chọn {key} {value} (cách 2 - button cặp)")
                except:
                    pass
        elif len(buttons) == 4:

            for idx, (key, value) in enumerate(results.items()):
                if idx >= len(buttons):
                    break
                btn = buttons[idx]
                btn_text = btn.text_content().strip()
                if btn_text == value:
                    try:
                        btn.click(force=True)
                        print(f"   ✅ Đã chọn {key} {value} (cách 2 - button đơn)")
                    except:
                        pass
        else:
            print("⚠️ Không tìm thấy đủ button, chuyển sang cách dùng XPath")


            for key, value in results.items():
                label_text = f"{key})"  
                xpath = f"//*[contains(text(), '{label_text}')]/following::button[contains(text(), '{value}')][1]"
                try:
                    btn = page.locator(xpath).first
                    if btn.is_visible(timeout=500):
                        btn.click(force=True)
                        print(f"   ✅ Đã chọn {key} {value} (cách 3 - XPath button)")
                        continue
                except:
                    pass

                xpath = f"//*[contains(text(), '{label_text}')]/following::label[contains(text(), '{value}')][1]"
                try:
                    lbl = page.locator(xpath).first
                    if lbl.is_visible(timeout=500):
                        lbl.click(force=True)
                        print(f"   ✅ Đã chọn {key} {value} (cách 3 - XPath label)")
                        continue
                except:
                    pass
                print(f"   ❌ Không tìm thấy nút cho {key} {value} (cách 3)")

def run_bot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("🚀 [Hệ thống] Đang khởi động trình duyệt và đăng nhập...")
        page.goto("https://app.onluyen.vn/login")

        try:
            page.fill("input[placeholder*='đăng nhập']", APP_USERNAME)
            page.fill("input[placeholder='Mật khẩu']", APP_PASSWORD)
            page.click("button:has-text('Đăng nhập')")
            page.wait_for_url("**/home-student", timeout=20000)
            print("✅ [Hệ thống] Login thành công!")
        except Exception as e:
            print(f"❌ [Hệ thống] Login thất bại: {e}")
            return

        page.goto(PRACTICE_URL)
        time.sleep(5)

        for i in range(1, 21):
            print(f"\n🔍 [Câu {i}] Đang quét nội dung...")
            time.sleep(2)

            input_selector = "input[type='text'], .input-fill-blank, [contenteditable='true']"
            input_field = page.locator(input_selector).first
            is_fill_blank = input_field.is_visible(timeout=2000)

            if is_fill_blank:
                print("📝 [Thông báo] Dạng bài: ĐIỀN Ô TRỐNG")
                q_content = page.evaluate("() => document.querySelector('.question-content-container')?.innerText || document.body.innerText")
                id_match = re.search(r"#(\d+)", q_content)
                q_id = id_match.group(1) if id_match else f"fill_{i}"

                ans = solve_question(q_content, is_fill_blank=True)
                if ans == "RETRY":
                    time.sleep(5)
                    ans = solve_question(q_content, is_fill_blank=True)

                log_question_to_file("question-dien-o.json", {"id": q_id, "question": q_content, "answer": ans})

                if ans:
                    print(f"⌨️ [Hệ thống] Đang điền: {ans}")
                    input_field.click()
                    input_field.fill("")
                    input_field.type(ans, delay=60)
                else:
                    print("⚠️ Không có đáp án, bỏ qua.")
                    try:
                        page.click("button:has-text('BỎ QUA')", timeout=3000)
                    except:
                        pass

            else:
                is_true_false = False
                try:
                    dung_btn = page.locator("text=Đúng").first
                    sai_btn = page.locator("text=Sai").first
                    if dung_btn.is_visible(timeout=1000) or sai_btn.is_visible(timeout=1000):
                        is_true_false = True
                        print("✅ [Thông báo] Dạng bài: ĐÚNG SAI")
                except:
                    pass

                if is_true_false:
                    q_content = page.evaluate("() => document.querySelector('.question-content-container')?.innerText || document.body.innerText")
                    id_match = re.search(r"#(\d+)", q_content)
                    q_id = id_match.group(1) if id_match else f"truefalse_{i}"

                    results = solve_true_false(q_content)
                    if results == "RETRY":
                        time.sleep(5)
                        results = solve_true_false(q_content)

                    log_question_to_file("question-dung-sai.json", {"id": q_id, "question": q_content, "answers": results})

                    if results:
                        click_true_false(page, results)
                    else:
                        print("⚠️ AI không trả về kết quả, bỏ qua")
                        try:
                            page.click("button:has-text('BỎ QUA')", timeout=3000)
                        except:
                            pass

                else:
                    print("🔘 [Thông báo] Dạng bài: KHOANH ĐÁP ÁN")
                    q_id, question, options = get_data_by_scraping(page)

                    log_question_to_file("questions.json", {"id": q_id, "question": question, "options": options})

                    ans = solve_question(question, options, is_fill_blank=False)
                    if ans == "RETRY":
                        time.sleep(5)
                        ans = solve_question(question, options, is_fill_blank=False)

                    if not ans:
                        print(f"⏭️ AI không trả lời được. Bỏ qua...")
                        try:
                            page.click("button:has-text('BỎ QUA')", timeout=3000)
                        except:
                            pass
                        continue

                    try:
                        print(f"🖱️ [Câu {i}] Đang click vào đáp án {ans}...")
                        choice_selectors = [
                            f"div.answer-item:has-text('{ans}')",
                            f"div.choice:has-text('{ans}')",
                            f"//div[contains(@class, 'answer')]//span[text()='{ans}']",
                            f"//div[contains(text(), '{ans}') and contains(@class, 'circle')]"
                        ]

                        is_clicked = False
                        for selector in choice_selectors:
                            target = page.locator(selector).first
                            if target.is_visible(timeout=1000):
                                target.click(force=True)
                                is_clicked = True
                                break

                        if not is_clicked:
                            target = page.locator(f"id=test-content >> text={ans}").first
                            if not target.is_visible():
                                target = page.get_by_text(ans, exact=True).last
                            box = target.bounding_box()
                            if box:
                                page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                                is_clicked = True

                        if is_clicked:
                            print(f"🎯 [Câu {i}] Click chọn {ans} thành công!")
                        else:
                            raise Exception("Không tìm thấy phần tử đáp án")
                    except Exception as e:
                        print(f"❌ [Câu {i}] Lỗi click: {e}")


            try:
                time.sleep(1.5)
                print(f"📩 [Câu {i}] Đang bấm 'TRẢ LỜI'...")
                confirm_btn = page.locator("button:has-text('TRẢ LỜI'), .btn-answer, button.primary").first
                confirm_btn.wait_for(state="visible", timeout=5000)
                confirm_btn.click(force=True)

                time.sleep(2)
                next_btn = page.locator("button:has-text('CÂU TIẾP THEO'), button:has-text('TIẾP TỤC'), .btn-next")
                if next_btn.is_visible():
                    next_btn.click(force=True)
                print(f"✨ [Câu {i}] Hoàn thành câu.")
            except Exception as e:
                print(f"❌ [Lỗi] {e}")
                page.screenshot(path=f"debug_cau{i}.png")
                try:
                    page.click("button:has-text('BỎ QUA')", timeout=3000)
                except:
                    pass

        print("\n🏁 [Hệ thống] Đã chạy xong 20 câu.")
        input("Nhấn Enter để đóng...")

if __name__ == "__main__":
    run_bot()