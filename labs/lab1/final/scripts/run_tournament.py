"""
Tu chay 1 "giai dau mini" mo phong dung cach thay cham: dung thang Arena / AgentLoader /
Environment cua framework (khong viet lai luat choi), voi cung cau hinh nhu de bai
(--capture-distance 2, --pacman-speed 2, --step-timeout 1.0, max_steps 200).

Nhom 0 dung ban FINAL (final/agent.py), doi thu la ban INITIAL cua tung nhom (24C05/source_code).
Moi doi thu danh 2 tran: nhom 0 lam Pacman, va nhom 0 lam Ghost.

Output:
  final/test_results/results_final_vs_initial.csv   (giong schema results.csv cua 24C05)
  final/test_results/error_log.txt                  (chi ghi khi co loi/timeout, giong error_log.txt cua 24C05)
  final/test_results/full_output.log                 (log day du tung tran, de doc lai khi can debug)
  In ra man hinh bang tong hop + so sanh voi so lieu chinh thuc cua ban initial (đã biết truoc).

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
STEP_TIMEOUT = 1.0  # giay - dung dung muc gioi han cua de bai, KHONG phai TIME_BUDGET rieng cua agent

# QUAN TRONG: mot vai doi thu (vd nhom 3, nhom 7) dung random.choice() KHONG seed rieng,
# nen ket qua tran cua ho khong tai lap duoc giua cac lan chay du vi tri xuat phat co dinh.
# Seed lai random truoc MOI tran de con chinh minh (0) so sanh "truoc/sau khi sua code"
# mot cach cong bang - neu khong se de nham lan thay doi cua doi thu la do minh gay ra.
RANDOM_SEED = 42

# So lieu chinh thuc cua nhom 0 o vong initial (lay tu 24C05/Checkpoint Result.xlsx, sheet summary)
# de so sanh truoc/sau ngay trong bao cao, khong can doc lai file xlsx moi lan chay.
OFFICIAL_INITIAL_0 = {
    "win_pacman": 15,
    "avg_pacman_steps": 9.666666667,
    "win_ghost": 2,
    "avg_ghost_steps": 23.93333333,
    "total_win": 17,
    "rank": 1,
}


def run_one_match(pacman_id, ghost_id, log_buffer):
    """Chay 1 tran, tra ve dict giong 1 dong cua results.csv. Khong bao gio raise/sys.exit."""
    random.seed(RANDOM_SEED)  # ep doi thu co random.choice() cung chay dinh nhu nhau moi lan
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
    except Exception as e:  # phong ngua tuyet doi khong de 1 tran loi lam sap ca giai
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

    # danh dau timeout ngay trong error de de loc, dung format giong error_log.txt cua 24C05
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
    print(f"\nDa chay {len(rows)} tran trong {elapsed:.1f}s")

    # --- ghi ket qua ---
    csv_path = RESULTS_DIR / "results_final_vs_initial.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pacman", "ghost", "winner_id", "winning_role", "total_steps", "error"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Da luu: {csv_path}")

    log_path = RESULTS_DIR / "full_output.log"
    log_path.write_text(full_log.getvalue(), encoding="utf-8")
    print(f"Da luu: {log_path}")

    error_log_path = RESULTS_DIR / "error_log.txt"
    with open(error_log_path, "w", encoding="utf-8") as f:
        f.write(f"ERROR LOG - Self-test tournament started, {len(rows)} matches\n")
        f.write("=" * 80 + "\n")
        if not error_entries:
            f.write("Khong co loi/timeout nao trong lan chay nay.\n")
        for pacman_id, ghost_id, err in error_entries:
            f.write(f"\nPACMAN: {pacman_id}\nGHOST: {ghost_id}\nERROR: {err}\n")
    print(f"Da luu: {error_log_path}")

    # --- tong hop so lieu nhom 0 ---
    as_pacman = [r for r in rows if r["pacman"] == US]
    as_ghost = [r for r in rows if r["ghost"] == US]

    win_pacman = [r for r in as_pacman if r["winning_role"] == "Pacman"]
    win_ghost = [r for r in as_ghost if r["winning_role"] == "Ghost"]

    missing_pacman = [r for r in as_pacman if r["total_steps"] == ""]
    missing_ghost = [r for r in as_ghost if r["total_steps"] == ""]
    if missing_pacman or missing_ghost:
        print(f"\nCANH BAO: {len(missing_pacman)} tran Pacman va {len(missing_ghost)} tran Ghost khong co "
              f"total_steps (load loi truoc khi choi) - trung binh ben duoi se bi lech thap hon thuc te, "
              f"xem {RESULTS_DIR / 'error_log.txt'} de biet chi tiet.")

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
    print(" SO SANH NHOM 0: BAN INITIAL (chinh thuc) vs BAN FINAL (tu test)")
    print("=" * 70)
    print(f"{'Chi so':<28}{'Initial (chinh thuc)':<24}{'Final (tu test)':<20}")
    print(f"{'Win as Pacman':<28}{OFFICIAL_INITIAL_0['win_pacman']:<24}{new_stats['win_pacman']:<20}")
    print(f"{'Avg Pacman Steps':<28}{OFFICIAL_INITIAL_0['avg_pacman_steps']:<24.3f}{new_stats['avg_pacman_steps']:<20.3f}")
    print(f"{'Win as Ghost':<28}{OFFICIAL_INITIAL_0['win_ghost']:<24}{new_stats['win_ghost']:<20}")
    print(f"{'Avg Ghost Steps':<28}{OFFICIAL_INITIAL_0['avg_ghost_steps']:<24.3f}{new_stats['avg_ghost_steps']:<20.3f}")
    print(f"{'Total Win':<28}{OFFICIAL_INITIAL_0['total_win']:<24}{new_stats['total_win']:<20}")
    print(f"\nLuu y: doi thu o day la ban INITIAL cua ho (chua toi uu). Ban optimized that cua ho")
    print("o vong final co the manh hon, ket qua nay chi la muc san khi ho CHUA sua loi/nang cap.")


if __name__ == "__main__":
    main()
