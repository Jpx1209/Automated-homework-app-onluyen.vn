import sys
import io


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import logging
import ai_engine
from bot import run_bot


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  
)


print("=" * 50)
print("Đang load file ai_engine:", ai_engine.__file__)
print("=" * 50)

logging.info("Bắt đầu chạy bot auto làm bài tập...")

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        logging.info("Bot đã bị dừng bởi người dùng (Ctrl+C).")
    except Exception as e:
        logging.exception("Bot gặp lỗi nghiêm trọng:")