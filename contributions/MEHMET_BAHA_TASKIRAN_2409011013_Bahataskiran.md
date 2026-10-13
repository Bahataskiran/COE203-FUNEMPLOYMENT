# Student Contribution Report

- **Name:** Mehmet Baha Taşkıran
- **Student ID:** 2409011013
- **GitHub Username:** Bahataskiran
- **Course:** COE203 - Advanced Programming (Project 1)

## My Contributions

### 1. Finding valid schedules
I worked on the main scheduling algorithm, especially the recursive `find_valid_schedules` function. It tries different course combinations and keeps the schedules that meet the requirements. I also added checks to stop exploring a branch when it cannot lead to a valid schedule, which helps avoid unnecessary work.

### 2. Checking time conflicts
I implemented the time-overlap check in `has_time_conflict`. The condition `start_a < end_b and start_b < end_a` is used to detect when two classes overlap. I also worked on checking schedules that include both lecture and lab sections.

### 3. Project structure and integration
I helped plan the main data structures used by the program, including lists of sections, tuples, and dictionaries for schedules. I also helped bring together the data reading, schedule sorting, and user interface parts.
