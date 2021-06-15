from typing import List, Tuple, Literal, Optional

import json
from courses import Course, Meeting, Selection, Time
import sys
from constraints import Constraint
from datetime import time
from os import listdir
from os.path import isfile, join

course_code = str
term = Literal["F", "S", "Y"]
selections = List[Tuple[course_code, term, Meeting]]


class Timetable:
    def __init__(self):
        # Works by every half hour.
        # index 5 refers to the time period from 02:30 to 03:00
        self.timetable_first: List[Optional[Meeting]] = [None] * 24 * 2 * 5
        self.timetable_second: List[Optional[Meeting]] = [None] * 24 * 2 * 5

        self.courses: List[Course] = []
        for f in listdir("courses"):
            loc = join("courses", f)
            if not isfile(loc):
                continue
            with open(loc) as course_file:
                self.courses.append(json.load(course_file))

    def all_timetables(self, past: List[Selection], ans: List[List[Selection]], index=0):
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
            for activity_code in term["meetings"]:
                curr_activity_meetings: List[Meeting] = []
                for meeting in term["meetings"][activity_code]:
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


res = Timetable().all_timetables([], [])
print(len(res))
