from timetable import Timetable

table = Timetable()
timetables = table.all_timetables()
flattened = []
for list_of_selections in timetables:
    total = []
    for selection in list_of_selections:
        for item in table.flatten_selection(selection):
            total.append(item)
    flattened.append(total)
filtered = table.sort_by_wasted_time(flattened)
times = {}
smallest = 100000
for selections in filtered:
    total = table.get_time(sorted(
        filter(lambda x: x.term in "FY", selections), key=table.sort_selection_comparator)) + table.get_time(sorted(
            filter(lambda x: x.term in "SY", selections), key=table.sort_selection_comparator))
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
