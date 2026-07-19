"""
Đồng bộ code vào một thư mục "bench" nằm đúng 2 cấp dưới pacman/ (giống hệt cấu trúc
pacman/submissions/<id>/agent.py) để mỗi agent.py tự resolve đúng sys.path của nó
(agent.py nào cũng tự tính src_path = Path(__file__).parent.parent.parent / "src").

Chạy lại script này bất cứ lúc nào sau khi sửa final/agent.py để bản bench được cập nhật.

Usage:
    python sync_bench.py
"""

import shutil
from pathlib import Path

LAB1_DIR = Path(__file__).resolve().parents[2]
FINAL_AGENT = LAB1_DIR / "final" / "agent.py"
SOURCE_CODE_DIR = LAB1_DIR / "24C05" / "source_code"
BENCH_DIR = LAB1_DIR / "HideSeek" / "pacman" / "bench_submissions"

OPPONENT_IDS = [str(i) for i in range(2, 17)]  # nhóm 2 .. 16 (bản initial)
# Lưu ý: một số nhóm (4, 13, 15) có file phụ ngoài agent.py (package riêng, module tách file)
# nên hàm sync() bên dưới copytree() nguyên thư mục thay vì chỉ copy 1 file agent.py.


def _clean_pycache(root: Path):
    for p in root.rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)


def sync():
    BENCH_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Nhóm 0 (bản final của chính mình) - luôn lấy bản mới nhất
    dst0 = BENCH_DIR / "0"
    if dst0.exists():
        shutil.rmtree(dst0)
    dst0.mkdir(parents=True)
    shutil.copy2(FINAL_AGENT, dst0 / "agent.py")
    print(f"[0]  final/agent.py -> {dst0 / 'agent.py'}")

    # 2. Các nhóm đối thủ - bản initial submission (không sửa gì)
    for sid in OPPONENT_IDS:
        src = SOURCE_CODE_DIR / sid
        if not src.exists():
            print(f"[{sid}] CẢNH BÁO: không tìm thấy {src}, bỏ qua")
            continue
        dst = BENCH_DIR / sid
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"[{sid}] {src} -> {dst}")

    _clean_pycache(BENCH_DIR)
    print(f"\nXong. Bench workspace: {BENCH_DIR}")


if __name__ == "__main__":
    sync()
