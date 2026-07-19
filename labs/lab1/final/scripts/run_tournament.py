"""
Tự chạy 1 "giải đấu mini" mô phỏng đúng cách thầy chấm: dùng thẳng Arena / AgentLoader /
Environment của framework (không viết lại luật chơi), với cùng cấu hình như đề bài
(--capture-distance 2, --pacman-speed 2, --step-timeout 1.0, max_steps 200).

Nhóm 0 dùng bản FINAL (final/agent.py), đối thủ là bản INITIAL của từng nhóm (24C05/source_code).
Mỗi đối thủ đánh 2 trận: nhóm 0 làm Pacman, và nhóm 0 làm Ghost.

Output:
  final/test_results/results_final_vs_initial.csv   (giống schema results.csv của 24C05)
  final/test_results/error_log.txt                  (chỉ ghi khi có lỗi/timeout, giống error_log.txt của 24C05)
  final/test_results/full_output.log                 (log đầy đủ từng trận, để đọc lại khi cần debug)
  In ra màn hình bảng tổng hợp + so sánh với số liệu chính thức của bản initial (đã biết trước).

Usage:
    python run_tournament.py
"""

import csv
import io
import random
import sys
import time
import traceback
from contextlib import redirect_stdout
from pathlib import Path

LAB1_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = LAB1_DIR / "HideSeek" / "pacman" / "src"
BENCH_DIR = LAB1_DIR / "HideSeek" / "pacman" / "bench_submissions"
RESULTS_DIR = LAB1_DIR / "final" / "test_results"

sys.path.insert(0, str(SRC_DIR))

from arena import Arena, AgentTimeoutError  # noqa: E402
from agent_loader import AgentLoadError  # noqa: E402

OPPONENT_IDS = [str(i) for i in range(2, 17)]
US = "0"

MAX_STEPS = 200
CAPTURE_DISTANCE = 2
PACMAN_SPEED = 2
STEP_TIMEOUT = 1.0  # giây - đúng đúng mức giới hạn của đề bài, KHÔNG phải TIME_BUDGET riêng của agent

# QUAN TRỌNG: một vài đối thủ (vd nhóm 3, nhóm 7) dùng random.choice() KHÔNG seed riêng,
# nên kết quả trận của họ không tái lập được giữa các lần chạy dù vị trí xuất phát cố định.
# Seed lại random trước MỖI trận để so chính mình (0) so sánh "trước/sau khi sửa code"
# một cách công bằng - nếu không sẽ dễ nhầm lẫn thay đổi của đối thủ là do mình gây ra.
RANDOM_SEED = 42

# Số liệu chính thức của nhóm 0 ở vòng initial (lấy từ 24C05/Checkpoint Result.xlsx, sheet summary)
# để so sánh trước/sau ngay trong báo cáo, không cần đọc lại file xlsx mỗi lần chạy.
OFFICIAL_INITIAL_0 = {
    "win_pacman": 15,
    "avg_pacman_steps": 9.666666667,
    "win_ghost": 2,
    "avg_ghost_steps": 23.93333333,
    "total_win": 17,
    "rank": 1,
}


def run_one_match(pacman_id, ghost_id, log_buffer):
    """Chạy 1 trận, trả về dict giống 1 dòng của results.csv. Không bao giờ raise/sys.exit."""
    random.seed(RANDOM_SEED)  # ép đối thủ có random.choice() cũng chạy y hệt nhau mỗi lần
    arena = Arena(
        pacman_id=pacman_id,
        ghost_id=ghost_id,
        submissions_dir=str(BENCH_DIR),
        max_steps=MAX_STEPS,
        visualize=False,
        step_timeout=STEP_TIMEOUT,
        deterministic_starts=True,
        capture_distance_threshold=CAPTURE_DISTANCE,
        pacman_speed=PACMAN_SPEED,
    )

    row = {
        "pacman": pacman_id,
        "ghost": ghost_id,
        "winner_id": "",
        "winning_role": "",
        "total_steps": "",
        "error": "",
    }

    try:
        with redirect_stdout(log_buffer):
            print(f"\n########## MATCH pacman={pacman_id} ghost={ghost_id} ##########")
            try:
                arena.pacman_agent = arena.loader.load_agent(
                    pacman_id, "pacman", init_kwargs={"pacman_speed": PACMAN_SPEED}
                )
                arena.ghost_agent = arena.loader.load_agent(ghost_id, "ghost")
            except AgentLoadError as e:
                print(f"LOAD ERROR: {e}")
                row["error"] = f"AGENT_LOAD_ERROR: {e}"
                return row

            result, stats = arena.run_game()
    except Exception as e:  # phòng ngừa tuyệt đối không để 1 trận lỗi làm sập cả giải
        print(f"UNEXPECTED ERROR: {e}")
        print(traceback.format_exc())
        row["error"] = f"UNEXPECTED_ERROR: {e}"
        return row

    total_steps = stats.get("total_steps", "")
    row["total_steps"] = total_steps

    if result == "pacman_wins":
        row["winner_id"] = pacman_id
        row["winning_role"] = "Pacman"
    elif result == "ghost_wins":
        row["winner_id"] = ghost_id
        row["winning_role"] = "Ghost"
    else:
        row["winner_id"] = ""
        row["winning_role"] = "Draw"

    # đánh dấu timeout ngay trong error để dễ lọc, đúng format giống error_log.txt của 24C05
    # ("timed out" là nguyên văn tiếng Anh do chính arena.py in ra, không phải nhãn tự đặt)
    log_text = log_buffer.getvalue()
    if "timed out" in log_text:
        row["error"] = "AGENT_TIMEOUT"

    return row


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    full_log = io.StringIO()
    error_entries = []

    start = time.time()
    for opp in OPPONENT_IDS:
        for pacman_id, ghost_id in [(US, opp), (opp, US)]:
            buf = io.StringIO()
            row = run_one_match(pacman_id, ghost_id, buf)
            rows.append(row)
            full_log.write(buf.getvalue())

            tag = "OK"
            if row["error"]:
                tag = row["error"].split(":")[0]
                error_entries.append((pacman_id, ghost_id, row["error"]))

            print(f"pacman={row['pacman']:>3} ghost={row['ghost']:>3} "
                  f"-> winner={row['winner_id'] or '-':>3} ({row['winning_role']:<6}) "
                  f"steps={row['total_steps']:<4} [{tag}]")

    elapsed = time.time() - start
    print(f"\nĐã chạy {len(rows)} trận trong {elapsed:.1f}s")

    # --- ghi kết quả ---
    csv_path = RESULTS_DIR / "results_final_vs_initial.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pacman", "ghost", "winner_id", "winning_role", "total_steps", "error"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Đã lưu: {csv_path}")

    log_path = RESULTS_DIR / "full_output.log"
    log_path.write_text(full_log.getvalue(), encoding="utf-8")
    print(f"Đã lưu: {log_path}")

    error_log_path = RESULTS_DIR / "error_log.txt"
    with open(error_log_path, "w", encoding="utf-8") as f:
        f.write(f"ERROR LOG - Self-test tournament started, {len(rows)} matches\n")
        f.write("=" * 80 + "\n")
        if not error_entries:
            f.write("Không có lỗi/timeout nào trong lần chạy này.\n")
        for pacman_id, ghost_id, err in error_entries:
            f.write(f"\nPACMAN: {pacman_id}\nGHOST: {ghost_id}\nERROR: {err}\n")
    print(f"Đã lưu: {error_log_path}")

    # --- tổng hợp số liệu nhóm 0 ---
    as_pacman = [r for r in rows if r["pacman"] == US]
    as_ghost = [r for r in rows if r["ghost"] == US]

    win_pacman = [r for r in as_pacman if r["winning_role"] == "Pacman"]
    win_ghost = [r for r in as_ghost if r["winning_role"] == "Ghost"]

    missing_pacman = [r for r in as_pacman if r["total_steps"] == ""]
    missing_ghost = [r for r in as_ghost if r["total_steps"] == ""]
    if missing_pacman or missing_ghost:
        print(f"\nCẢNH BÁO: {len(missing_pacman)} trận Pacman và {len(missing_ghost)} trận Ghost không có "
              f"total_steps (load lỗi trước khi chơi) - trung bình bên dưới sẽ bị lệch thấp hơn thực tế, "
              f"xem {RESULTS_DIR / 'error_log.txt'} để biết chi tiết.")

    avg_pacman_steps = sum(int(r["total_steps"]) for r in as_pacman if r["total_steps"] != "") / len(as_pacman)
    avg_ghost_steps = sum(int(r["total_steps"]) for r in as_ghost if r["total_steps"] != "") / len(as_ghost)

    new_stats = {
        "win_pacman": len(win_pacman),
        "avg_pacman_steps": avg_pacman_steps,
        "win_ghost": len(win_ghost),
        "avg_ghost_steps": avg_ghost_steps,
        "total_win": len(win_pacman) + len(win_ghost),
    }

    print("\n" + "=" * 70)
    print(" SO SÁNH NHÓM 0: BẢN INITIAL (chính thức) vs BẢN FINAL (tự test)")
    print("=" * 70)
    print(f"{'Chỉ số':<28}{'Initial (chính thức)':<24}{'Final (tự test)':<20}")
    print(f"{'Win as Pacman':<28}{OFFICIAL_INITIAL_0['win_pacman']:<24}{new_stats['win_pacman']:<20}")
    print(f"{'Avg Pacman Steps':<28}{OFFICIAL_INITIAL_0['avg_pacman_steps']:<24.3f}{new_stats['avg_pacman_steps']:<20.3f}")
    print(f"{'Win as Ghost':<28}{OFFICIAL_INITIAL_0['win_ghost']:<24}{new_stats['win_ghost']:<20}")
    print(f"{'Avg Ghost Steps':<28}{OFFICIAL_INITIAL_0['avg_ghost_steps']:<24.3f}{new_stats['avg_ghost_steps']:<20.3f}")
    print(f"{'Total Win':<28}{OFFICIAL_INITIAL_0['total_win']:<24}{new_stats['total_win']:<20}")
    print(f"\nLưu ý: đối thủ ở đây là bản INITIAL của họ (chưa tối ưu). Bản optimized thật của họ")
    print("ở vòng final có thể mạnh hơn, kết quả này chỉ là mức sàn khi họ CHƯA sửa lỗi/nâng cấp.")


if __name__ == "__main__":
    main()
