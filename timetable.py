from typing import List, Tuple, Literal, Optional

import json
from courses import Course, Meeting, Selection, Time, Term, FlattenedSelection
import sys
from constraints import Constraint
from datetime import time
from os import listdir
from os.path import isfile, join
from constraints import Constraint

course_code = str
term = Literal["F", "S", "Y"]
selections = List[Tuple[course_code, term, Meeting]]


class Timetable:
    def __init__(self):
        # Works by every half hour.
        # index 5 refers to the time period from 02:30 to 03:00
        self.timetable_first: List[Optional[Meeting]] = [None] * 24 * 2 * 5
        self.timetable_second: List[Optional[Meeting]] = [None] * 24 * 2 * 5

        with open("./constraints.json") as constraint_f:
            self.constraint: Constraint = json.load(constraint_f)

        self.courses: List[Course] = []

        smallest_time = time.fromisoformat(
            self.constraint["smallest_start_time"])
        biggest_time = time.fromisoformat(
            self.constraint["biggest_end_time"])

        for f in listdir("courses"):
            loc = join("courses", f)
            if not isfile(loc):
                continue
            with open(loc) as course_file:
                self.courses.append(json.load(course_file))

        # Filtering stuff based on constraints
        course_constraints = self.constraint["course_constraint"]
        for course in self.courses:
            all_terms: List[Term] = []
            code = course["code"]
            for term in course["terms"]:
                if (code in course_constraints
                        and term["term"] != course_constraints[code]["term"]):
                    continue
                all_terms.append(term)
                for activity_type in term["meetings"]:
                    meetings = term["meetings"][activity_type]
                    filtered: List[Meeting] = []
                    for meeting in meetings:
                        is_good_meeting = True
                        if code in course_constraints:
                            for section in course_constraints[code]["exclude"]:
                                activity_type = section[0:3]
                                activity_code = section[3:]
                                if activity_code == meeting["activity_code"] and activity_type == meeting["activity_type"]:
                                    is_good_meeting = False
                                    break
                        if not is_good_meeting:
                            continue
                        for t in meeting["times"]:
                            if t["start"] == "None":
                                continue
                            start = time.fromisoformat(t["start"])
                            end = time.fromisoformat(t["end"])
                            if smallest_time > start or biggest_time < end:
                                is_good_meeting = False
                                break
                        if is_good_meeting:
                            filtered.append(meeting)

                    term["meetings"][activity_type] = filtered
            course["terms"] = all_terms

    def all_timetables(self, past: List[Selection] = [], ans: List[List[Selection]] = [], index=0) -> List[List[Selection]]:
        if index == len(self.courses):
            if index != 0:
                ans.append(past[:])
        else:
            curr = self.get_possible_selections(index)
            for selection in curr:
                past.append(selection)
                self.add_to_timetable(selection)
                self.all_timetables(past, ans, index + 1)
                self.remove_from_timetable(selection)
                past.pop()
        return ans

    def add_to_timetable(self, selection: Selection):
        term = selection["term"]
        for meeting in selection["meetings"]:
            for time in meeting["times"]:
                start, end = self.time_to_index(time)
                if start == -1:
                    continue
                for i in range(start, end):
                    if ((term in "FY" and self.timetable_first[i] is not None)
                            or (term in "SY" and self.timetable_second[i] is not None)):
                        raise Exception(
                            f"""Trying to add to timetable when slot is used:
                            {json.dumps([selection, self.timetable_first, self.timetable_second])}""")
                    if term in "FY":
                        self.timetable_first[i] = selection
                    if term in "SY":
                        self.timetable_second[i] = selection

    def remove_from_timetable(self, selection: Selection):
        term = selection["term"]
        for meeting in selection["meetings"]:
            for time in meeting["times"]:
                start, end = self.time_to_index(time)
                if start == -1:
                    continue
                for i in range(start, end):
                    if ((term in "FY" and self.timetable_first[i] is None)
                            or (term in "SY" and self.timetable_second[i] is None)):
                        raise Exception(
                            f"""Trying to remove to timetable when slot isn't used:
                            {json.dumps([selection, self.timetable_first, self.timetable_second])}""")
                    if term in "FY":
                        self.timetable_first[i] = None
                    if term in "SY":
                        self.timetable_second[i] = None

    def get_possible_selections(self, index: int) -> List[Selection]:
        def get_combinations(so_far: List[Selection],
                             remaining: List[List[Meeting]]) -> List[Selection]:
            if len(remaining) == 0:
                return so_far
            new_so_far = []
            for item in so_far:
                for other in remaining[0]:
                    if self.check_overlap_with_selection(item, other):
                        continue
                    ori = {
                        "code": item["code"],
                        "term": item["term"],
                        "meetings": item["meetings"][:]
                    }
                    ori["meetings"].append(other)
                    new_so_far.append(ori)

            return get_combinations(new_so_far, remaining[1:])

        curr_course = self.courses[index]
        ans: List[Selection] = []
        for term in curr_course["terms"]:
            all_activities: List[List[Meeting]] = []
            for activity_type in term["meetings"]:
                curr_activity_meetings: List[Meeting] = []
                for meeting in term["meetings"][activity_type]:
                    if not self.check_overlap(term["term"], meeting):
                        curr_activity_meetings.append(meeting)
                all_activities.append(curr_activity_meetings)
            if len(all_activities) > 0:
                ans += get_combinations([{
                    "code": curr_course["code"],
                    "term": term["term"],
                    "meetings": [item]}
                    for item in all_activities[0]], all_activities[1:])
        return ans

    def check_overlap_with_selection(self, prev: Selection, new_meeting: Meeting) -> bool:
        for meeting in prev["meetings"]:
            for time1 in meeting["times"]:
                if time1["start"] == "None":  # Async timetable case
                    continue
                start1 = time.fromisoformat(time1["start"])
                end1 = time.fromisoformat(time1["end"])
                day1 = time1["day_of_week"].lower()
                for time2 in new_meeting["times"]:
                    if time2["start"] == "None":  # Async timetable case
                        continue
                    start2 = time.fromisoformat(time2["start"])
                    end2 = time.fromisoformat(time2["end"])
                    day2 = time2["day_of_week"].lower()
                    if day1 == day2 and start1 < end2 and end1 > start2:
                        return True
        return False

    def time_to_index(self, time: Time) -> int:
        if time["start"] == "None":  # Async timetable case
            return -1, -1
        index = 0
        day = time["day_of_week"].lower()
        if day == "monday":
            index += 0
        elif day == "tuesday":
            index += 48
        elif day == "wednesday":
            index += 96
        elif day == "thursday":
            index += 144
        elif day == "friday":
            index += 192
        else:
            raise Exception(f"Could not find day of week: {time}")
        start_hour, start_minute = time["start"].split(":")
        end_hour, end_minute = time["end"].split(":")
        start = index + int(start_hour) * 2 + (start_minute == "30")
        end = index + int(end_hour) * 2 + (end_minute == "30")
        return start, end

    def check_overlap(self, term: str, meeting: Meeting) -> bool:
        time_periods: List[int] = []
        for time in meeting["times"]:
            start, end = self.time_to_index(time)
            if start == -1:  # Async timetable case
                return False
            for i in range(start, end):
                if ((term in "FY" and self.timetable_first[i] is not None)
                        or (term in "SY" and self.timetable_second[i] is not None)):
                    return True
        return False

    def flatten_selection(self, selection: Selection) -> List[FlattenedSelection]:
        ans = []
        for meeting in selection["meetings"]:
            for t in meeting["times"]:
                ans.append({
                    "code": selection["code"],
                    "term": selection["term"],
                    "instructors": [item.strip() for item in meeting["instructors"].split("\n")],
                    "space": meeting["space"],
                    "waitlist": meeting["waitlist"],
                    "notes": meeting["notes"],
                    "day_of_week": t["day_of_week"],
                    "start": t["start"],
                    "end": t["end"],
                    "activity": meeting["activity_type"] + meeting["activity_code"]
                })
        return ans

    def display_nicely(self, selections: List[FlattenedSelection]) -> str:
        ans = []
        first = sorted(
            filter(lambda x: x["term"] in "FY", selections), key=self.sort_selection_comparator)
        second = sorted(
            filter(lambda x: x["term"] in "SY", selections), key=self.sort_selection_comparator)
        ans.append("—————————————————————————————————————————————")
        for s in first:
            ans.append(
                f"{s['code']}-{s['term']} {s['activity']} on {s['day_of_week']}, {s['start']} to {s['end']}")
        ans.append("—————————————————————————————————————————————")
        for s in second:
            ans.append(
                f"{s['code']}-{s['term']} {s['activity']} on {s['day_of_week']}, {s['start']} to {s['end']}")
        ans.append("—————————————————————————————————————————————")
        return "\n".join(ans)

    def get_time(self, selections: List[FlattenedSelection]) -> int:
        total_time = 0
        visited_weekdays = set()
        for item in selections:
            visited_weekdays.add(item["day_of_week"])
        days = ["monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday"]
        for item in visited_weekdays:
            if item.lower() in days:
                total_time += self.constraint["commute_time"]
        for i in range(len(selections) - 1):
            item = selections[i]
            item_after = selections[i+1]
            day = item["day_of_week"].lower()
            day_after = item_after["day_of_week"].lower()
            if day not in days:
                break
            elif day == day_after:
                hour1, minute1 = item_after["start"].split(":")
                hour2, minute2 = item["end"].split(":")
                total_time += ((int(hour1) * 60 + int(minute1)) -
                               (int(hour2) * 60 + int(minute2)))
        return total_time

    def sort_selection_comparator(self, s: Selection):
        weekday_to_int = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4
        }
        if s["start"] == "None":
            return (100, 100)
        day = weekday_to_int[s["day_of_week"].lower()]
        start = time.fromisoformat(s["start"])
        end = time.fromisoformat(s["end"])
        return (day, start)

    def sort_by_wasted_time(self, items: List[List[FlattenedSelection]]) -> List[List[FlattenedSelection]]:
        def comparator(selections: List[FlattenedSelection]):
            return self.get_time(sorted(
                filter(lambda x: x["term"] in "FY", selections), key=self.sort_selection_comparator)) + self.get_time(sorted(
                    filter(lambda x: x["term"] in "SY", selections), key=self.sort_selection_comparator))
        return sorted(items, key=comparator)


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
        filter(lambda x: x["term"] in "FY", selections), key=table.sort_selection_comparator)) + table.get_time(sorted(
            filter(lambda x: x["term"] in "SY", selections), key=table.sort_selection_comparator))
    if total not in times:
        times[total] = []
    times[total].append(selections)
    if total < smallest:
        smallest = total
if len(filtered) == 0:
    print("No timetables found")
else:
    curr = 1
    print(
        f"Currently displaying: {curr}/{len(times[smallest])}")
    print(table.display_nicely(times[smallest][0]))
    item = input("Enter to go forward, 1 to exit, 0 to go back\n")
    print("\n\n\n")
    while item != "1":
        if item == "0":
            if curr > 1:
                curr -= 1
        else:
            curr += 1
        print(
            f"Currently displaying: {curr}/{len(times[smallest])}")
        print(table.display_nicely(times[smallest][curr - 1]))
        item = input("Enter to go forward, 1 to exit, 0 to go back\n")
        print("\n\n\n")
