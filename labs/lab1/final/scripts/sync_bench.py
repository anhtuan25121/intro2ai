"""
Dong bo code vao mot thu muc "bench" nam dung 2 cap duoi pacman/ (giong het cau truc
pacman/submissions/<id>/agent.py) de moi agent.py tu resolve dung sys.path cua no
(agent.py nao cung tu tinh src_path = Path(__file__).parent.parent.parent / "src").

Chay lai script nay bat cu luc nao sau khi sua final/agent.py de ban bench duoc cap nhat.

Usage:
    python sync_bench.py
"""

import shutil
from pathlib import Path

LAB1_DIR = Path(__file__).resolve().parents[2]
FINAL_AGENT = LAB1_DIR / "final" / "agent.py"
SOURCE_CODE_DIR = LAB1_DIR / "24C05" / "source_code"
BENCH_DIR = LAB1_DIR / "HideSeek" / "pacman" / "bench_submissions"

OPPONENT_IDS = [str(i) for i in range(2, 17)]  # nhom 2 .. 16 (ban initial)
# Luu y: mot so nhom (4, 13, 15) co file phu ngoai agent.py (package rieng, module tach file)
# nen ham sync() ben duoi copytree() nguyen thu muc thay vi chi copy 1 file agent.py.


def _clean_pycache(root: Path):
    for p in root.rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)


def sync():
    BENCH_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Nhom 0 (ban final cua chinh minh) - luon lay ban moi nhat
    dst0 = BENCH_DIR / "0"
    if dst0.exists():
        shutil.rmtree(dst0)
    dst0.mkdir(parents=True)
    shutil.copy2(FINAL_AGENT, dst0 / "agent.py")
    print(f"[0]  final/agent.py -> {dst0 / 'agent.py'}")

    # 2. Cac nhom doi thu - ban initial submission (khong sua gi)
    for sid in OPPONENT_IDS:
        src = SOURCE_CODE_DIR / sid
        if not src.exists():
            print(f"[{sid}] CANH BAO: khong tim thay {src}, bo qua")
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
