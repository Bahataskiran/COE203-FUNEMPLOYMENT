"""
Course Schedule Optimizer (COE203 - Project 1)

This script loads university course schedule data from an Excel workbook,
filters theoretical lectures and lab sessions (sections >= 51), checks for
time and day conflicts, and generates optimal conflict-free weekly schedules
based on custom user optimization preferences.
"""

import os
import openpyxl

DEFAULT_EXCEL_FILENAME = "26-27-guz-yari-yili-ders-plani-2.xlsx"
LAB_SECTION_THRESHOLD = 51
DAY_ORDER = {"Pazartesi": 1, "Salı": 2, "Çarşamba": 3, "Perşembe": 4, "Cuma": 5}


# ============================================================================
# HELPER FUNCTIONS: DATA PARSING & CONFLICT CHECKS
# ============================================================================

def parse_time_to_minutes(time_str):
    """Converts a time string in 'HH:MM' format into total minutes from midnight."""
    clean_str = str(time_str).strip()
    if not clean_str or ":" not in clean_str:
        return -1
    parts = clean_str.split(":")
    if len(parts) != 2:
        return -1
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        return -1


def has_time_conflict(session_a, session_b):
    """Checks whether two course sessions collide on the same day and time interval."""
    if session_a["gun"].strip().lower() != session_b["gun"].strip().lower():
        return False

    start_a = parse_time_to_minutes(session_a["baslangic"])
    end_a = parse_time_to_minutes(session_a["bitis"])
    start_b = parse_time_to_minutes(session_b["baslangic"])
    end_b = parse_time_to_minutes(session_b["bitis"])

    if -1 in (start_a, end_a, start_b, end_b):
        return False
        
    return (start_a < end_b) and (start_b < end_a)


def load_courses_from_excel(filename):
    """Loads course data from an Excel file and returns them as a list of dictionaries."""
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, filename)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Excel file '{filename}' was not found in the project folder!")

    workbook = openpyxl.load_workbook(file_path, data_only=True)
    sheet = workbook.active
    course_list = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue

        raw_code, raw_sube, raw_gun, raw_baslangic, raw_bitis = row[:5]

        try:
            section_number = int(raw_sube)
        except (ValueError, TypeError):
            section_number = 1

        record = {
            "ders_kodu": str(raw_code).strip().upper(),
            "sube": section_number,
            "gun": str(raw_gun).strip().capitalize() if raw_gun else "",
            "baslangic": str(raw_baslangic).strip() if raw_baslangic else "",
            "bitis": str(raw_bitis).strip() if raw_bitis else "",
        }
        course_list.append(record)

    return course_list


def separate_theory_and_labs(selected_codes, all_courses):
    """Separates selected courses into theory and lab option lists."""
    categorized = {}
    for code in selected_codes:
        theory = []
        labs = []
        for entry in all_courses:
            if entry["ders_kodu"] == code:
                if entry["sube"] >= LAB_SECTION_THRESHOLD:
                    labs.append(entry)
                else:
                    theory.append(entry)
        categorized[code] = {"teorik": theory, "lab": labs}
    return categorized


def find_valid_schedules(unit_pools, current_schedule=None, index=0):
    """
    Finds all valid, conflict-free course schedules using the Backtracking algorithm.

    Logic:
      1. Choose: Try adding an available section of the current course.
      2. Check: Verify that it does not conflict with previously selected courses.
      3. Recurse: Move to the next course (index + 1).
      4. Backtrack: Remove the last chosen section (pop) to try alternative options.
    """
    if current_schedule is None:
        current_schedule = []

    if index == len(unit_pools):
        return [list(current_schedule)]

    valid_results = []
    pool_name, options = unit_pools[index]

    for candidate in options:
        conflict = False
        for scheduled in current_schedule:
            if has_time_conflict(candidate, scheduled):
                conflict = True
                break

        if not conflict:
            current_schedule.append(candidate)
            sub_results = find_valid_schedules(unit_pools, current_schedule, index + 1)
            valid_results.extend(sub_results)
            current_schedule.pop()

    return valid_results


# ============================================================================
# HELPER FUNCTIONS: OPTIMIZATION METRICS
# ============================================================================

def calculate_total_days(schedule):
    """Returns the total number of distinct campus days in a given schedule."""
    return len(set(session["gun"] for session in schedule))


def calculate_latest_start_score(schedule):
    """Calculates a score tuple to prioritize schedules that start as late as possible."""
    day_starts = {}

    for session in schedule:
        day = session["gun"]
        start_min = parse_time_to_minutes(session["baslangic"])

        if start_min != -1:
            if day not in day_starts or start_min < day_starts[day]:
                day_starts[day] = start_min

    if not day_starts:
        return (0, 0)

    earliest_day_start = min(day_starts.values())
    avg_start = sum(day_starts.values()) / len(day_starts)

    return (earliest_day_start, avg_start)


def calculate_total_idle_time(schedule):
    """Calculates the total idle waiting time between classes on the same day in minutes."""
    days_map = {}

    for session in schedule:
        day = session["gun"]
        start = parse_time_to_minutes(session["baslangic"])
        end = parse_time_to_minutes(session["bitis"])

        if start != -1 and end != -1:
            days_map.setdefault(day, []).append((start, end))

    total_gap = 0

    for day, intervals in days_map.items():
        intervals.sort(key=lambda x: x[0])

        for i in range(len(intervals) - 1):
            current_end = intervals[i][1]
            next_start = intervals[i + 1][0]

            if next_start > current_end:
                total_gap += (next_start - current_end)

    return total_gap


def format_schedule_report(schedule, plan_index=1):
    """Formats schedule details and metrics into a readable terminal table."""
    unique_days = set(session["gun"] for session in schedule)
    days_used = sorted(list(unique_days), key=lambda d: DAY_ORDER.get(d, 99))

    earliest_start, avg_start = calculate_latest_start_score(schedule)

    earliest_h = int(earliest_start // 60)
    earliest_m = int(earliest_start % 60)
    avg_h = int(avg_start // 60)
    avg_m = int(avg_start % 60)
    idle_hours = calculate_total_idle_time(schedule) / 60

    report = [
        "\n" + "=" * 60,
        f"  OPTION #{plan_index}",
        f"  -> Total Campus Days      : {len(days_used)} days ({', '.join(days_used)})",
        f"  -> Earliest Class Start   : {earliest_h:02d}:{earliest_m:02d} (Average: {avg_h:02d}:{avg_m:02d})",
        f"  -> Total Gap Time Between : {idle_hours:.1f} hours",
        "=" * 60,
    ]

    schedule_sorted = sorted(
        schedule, 
        key=lambda x: (DAY_ORDER.get(x["gun"], 99), parse_time_to_minutes(x["baslangic"]))
    )

    for session in schedule_sorted:
        session_type = "LAB" if session["sube"] >= LAB_SECTION_THRESHOLD else "LECTURE"
        report.append(
            f"  [{session['ders_kodu']}] Section {session['sube']:<2} ({session_type:<7}) | {session['gun']:<10} {session['baslangic']} - {session['bitis']}"
        )

    return "\n".join(report)


# ============================================================================
# MAIN APPLICATION CONTROLLER
# ============================================================================

def main():
    print("=" * 60)
    print("       COURSE SCHEDULE OPTIMIZATION SYSTEM")
    print("=" * 60)

    try:
        courses = load_courses_from_excel(DEFAULT_EXCEL_FILENAME)
        print(f"-> Excel loaded successfully. Total records: {len(courses)}\n")
    except FileNotFoundError as error:
        print(f"-> ERROR: {error}")
        return

    # 1. Get Course Selections from User
    selected_codes = []
    print("Enter the course codes you want to take (e.g., COE203, SWE209).")
    print("Press ENTER on an empty line when you are done.\n")

    while True:
        entry = input(f"Course #{len(selected_codes) + 1} Code: ").strip().upper()
        if not entry:
            break
        if entry in selected_codes:
            print(f"   -> '{entry}' is already added.")
            continue
        if not any(c["ders_kodu"] == entry for c in courses):
            print(f"   -> Warning: '{entry}' not found in Excel! Please check again.")
            continue
        selected_codes.append(entry)

    if not selected_codes:
        print("-> No courses selected. Program terminated.")
        return

    # 2. Separate Theory and Labs
    separated = separate_theory_and_labs(selected_codes, courses)
    unit_pools = []
    for code, groups in separated.items():
        if groups["teorik"]:
            unit_pools.append((f"{code}_THEORY", groups["teorik"]))
        if groups["lab"]:
            unit_pools.append((f"{code}_LAB", groups["lab"]))

    print(f"\n-> Total course components to schedule: {len(unit_pools)} (Theory + Lab)")

    # 3. Find Conflict-Free Schedules
    viable_schedules = find_valid_schedules(unit_pools)
    if not viable_schedules:
        print("\n-> NO CONFLICT-FREE SCHEDULE FOUND FOR SELECTED COURSES!")
        print("   Please review your course or section selections.")
        return

    print(f"\n[SUCCESS] Found {len(viable_schedules)} valid schedule combinations.")

    # 4. Optimization Preference Menu
    print("\n" + "-" * 50)
    print("CHOOSE YOUR OPTIMIZATION PREFERENCE:")
    print(" [1] Minimum Days       : Attend campus as few days as possible")
    print(" [2] Latest Start       : Avoid early mornings (Late start)")
    print(" [3] Earliest Start     : Finish the day early (Early start)")
    print(" [4] Compact Schedule   : Minimize waiting gaps between classes")
    print("-" * 50)

    choice = input("Your choice (1/2/3/4) [Default: 1]: ").strip()

    if choice == "2":
        viable_schedules.sort(key=calculate_latest_start_score, reverse=True)
        print("\n-> Schedules sorted by: LATEST START TIME.")
    elif choice == "3":
        viable_schedules.sort(key=lambda s: calculate_latest_start_score(s)[1])
        print("\n-> Schedules sorted by: EARLIEST START TIME.")
    elif choice == "4":
        viable_schedules.sort(key=calculate_total_idle_time)
        print("\n-> Schedules sorted by: MINIMUM GAP TIME (Compact).")
    else:
        viable_schedules.sort(key=lambda s: (calculate_total_days(s), calculate_total_idle_time(s)))
        print("\n-> Schedules sorted by: FEWEST CAMPUS DAYS.")

    # Display Top 3 Schedules
    print("\nTOP 3 SCHEDULE OPTIONS:")
    for i, plan in enumerate(viable_schedules[:3], start=1):
        print(format_schedule_report(plan, plan_index=i))


if __name__ == "__main__":
    main()
