from timetable import Timetable

table = Timetable()
filtered = table.sort_by_wasted_time(table.flatten_timetables(
    table.all_timetables()))
times = {}
smallest = 100000
for selections in filtered:
    total = table.get_time_unsplit(selections)
    if total not in times:
        times[total] = []
    times[total].append(selections)
    if total < smallest:
        smallest = total
if len(filtered) == 0:
    print("No possible timetable can be generated with current constraints and courses")
else:
    curr = 1
    print(
        f"Currently displaying: {curr}/{len(times[smallest])} with {smallest} hours wasted per week (both terms)")
    print(table.display_nicely(times[smallest][0]))
    item = input("Enter to go forward, 1 to exit, 0 to go back\n")
    while item != "1":
        print("\n\n\n")
        if item == "0":
            if curr > 1:
                curr -= 1
        else:
            if curr < len(times[smallest]):
                curr += 1
        print(
            f"Currently displaying: {curr}/{len(times[smallest])} with {smallest/60} hours wasted per week (both terms)")
        print(table.display_nicely(times[smallest][curr - 1]))
        item = input("Enter to go forward, 1 to exit, 0 to go back\n")
