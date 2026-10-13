# Course Schedule Optimizer
# Course Schedule Optimizer - COE203 Project 1

A Python tool that generates conflict-free weekly course schedules from the university timetable Excel file. It handles both lecture and lab sections and sorts valid schedules based on your preference.

## Files in this Repository

- main.py: Interactive script where you type courses and choose preferences step by step.
- cli.py: Non-interactive CLI version that takes arguments directly (uses argparse).
- requirements.txt: Required dependencies (openpyxl).
- contributions/: Folder containing markdown reports for each group member.
- 26-27-guz-yari-yili-ders-plani-2.xlsx: Timetable data source.

## Setup

First, make sure dependencies are installed:

pip install -r requirements.txt

## Usage

### 1. Command Line Interface (CLI)
You can run cli.py by passing course codes and an optional sorting criteria:

# Basic run (default: minimum days)
python cli.py --courses COE203 SWE209

# Sort by latest start time
python cli.py --courses COE203 SWE209 --criteria 2

# Show top 5 options
python cli.py --courses COE203 SWE209 MATH101 --criteria 4 --top 5

# See all arguments
python cli.py --help

### 2. Interactive Mode
If you prefer terminal prompts:

python main.py

## Optimization Preferences

1. Minimum Days (1): Attends campus on as few days as possible.
2. Latest Start (2): Avoids early morning lectures.
3. Earliest Start (3): Prioritizes early starts to finish earlier in the day.
4. Compact Schedule (4): Minimizes waiting gaps between classes on the same day.

## Group Members

- Mehmet Baha Taşkıran (2409011013) - @Bahataskiran
- Muhammet Emin Bakırcı (2409111037) - @Eminbakircii
- Yunus Çerkezoğlu (2409011003) - @yunuscerkezoglu
- Mehmet Ali Saray (2509011054) - @MehmetAliS480
- Sinan İnan (2409011034) - @sinaninan
