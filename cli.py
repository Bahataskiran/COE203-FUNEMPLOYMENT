"""
Command Line Interface (CLI) for Course Schedule Optimizer
Course: COE203 - Project 1

Usage Examples:
    python cli.py --courses COE203 SWE209 --criteria 1
    python cli.py --courses COE203 MATH101 SWE209 --criteria 2 --top 5
"""

import argparse
import sys

# main.py içindeki hazır fonksiyonları çağırıyoruz
from main import (
    load_courses_from_excel,
    separate_theory_and_labs,
    find_valid_schedules,
    calculate_total_days,
    calculate_latest_start_score,
    calculate_total_idle_time,
    format_schedule_report,
    DEFAULT_EXCEL_FILENAME,
)


def parse_arguments():
    """Parses command-line arguments using argparse (Week 3 - Slides 28-31)."""
    parser = argparse.ArgumentParser(
        description="Automated Course Schedule Optimizer (COE203)",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Slayt 28 & 43: nargs="+" ile birden fazla ders kodu listesi alma
    parser.add_argument(
        "--courses",
        nargs="+",
        required=True,
        help="List of course codes to enroll (e.g., --courses COE203 SWE209)",
    )

    # Slayt 31: type=int ve choices ile girdi sınırlama (Robustness)
    parser.add_argument(
        "--criteria",
        type=int,
        choices=[1, 2, 3, 4],
        default=1,
        help=(
            "Optimization objective:\n"
            "  1: Minimum Days (Fewest campus days)\n"
            "  2: Latest Start (Avoid early mornings)\n"
            "  3: Earliest Start (Finish day early)\n"
            "  4: Compact Schedule (Minimize gaps)\n"
            "Default is 1."
        ),
    )

    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of schedule options to display (Default: 3)",
    )

    parser.add_argument(
        "--excel",
        type=str,
        default=DEFAULT_EXCEL_FILENAME,
        help=f"Excel file path (Default: {DEFAULT_EXCEL_FILENAME})",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print("=" * 60)
    print("       COURSE SCHEDULE OPTIMIZER - CLI MODE")
    print("=" * 60)

    # 1. Excel Yükleme
    try:
        courses = load_courses_from_excel(args.excel)
    except FileNotFoundError as err:
        print(f"[FATAL ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    # 2. Ders Kodlarını Doğrulama (Hocanın kırmaya çalışmasına karşı koruma)
    available_codes = set(c["ders_kodu"] for c in courses)
    valid_codes = []
    missing_codes = []

    for code in [c.strip().upper() for c in args.courses]:
        if code in available_codes:
            if code not in valid_codes:
                valid_codes.append(code)
        else:
            missing_codes.append(code)

    if missing_codes:
        print(f"[WARNING] Courses not found in Excel: {', '.join(missing_codes)}")

    if not valid_codes:
        print("[ERROR] No valid course codes provided. Exiting.", file=sys.stderr)
        sys.exit(1)

    print(f"-> Selected courses: {', '.join(valid_codes)}")

    # 3. Şube Ayrımı
    separated = separate_theory_and_labs(valid_codes, courses)
    unit_pools = []
    for code, groups in separated.items():
        if groups["teorik"]:
            unit_pools.append((f"{code}_THEORY", groups["teorik"]))
        if groups["lab"]:
            unit_pools.append((f"{code}_LAB", groups["lab"]))

    # 4. Çakışmasız Planları Bul
    viable_schedules = find_valid_schedules(unit_pools)
    if not viable_schedules:
        print("\n[RESULT] No conflict-free schedules found for these courses.")
        sys.exit(0)

    print(f"-> Found {len(viable_schedules)} valid schedule combination(s).")

    # 5. Sıralama Kriteri
    if args.criteria == 2:
        viable_schedules.sort(key=calculate_latest_start_score, reverse=True)
    elif args.criteria == 3:
        viable_schedules.sort(key=lambda s: calculate_latest_start_score(s)[1])
    elif args.criteria == 4:
        viable_schedules.sort(key=calculate_total_idle_time)
    else:
        viable_schedules.sort(key=lambda s: (calculate_total_days(s), calculate_total_idle_time(s)))

    # 6. Rapor Yazdırma
    count_to_show = max(1, args.top)
    print(f"\nTOP {min(count_to_show, len(viable_schedules))} SCHEDULE OPTION(S):")
    for i, plan in enumerate(viable_schedules[:count_to_show], start=1):
        print(format_schedule_report(plan, plan_index=i))


if __name__ == "__main__":
    main()