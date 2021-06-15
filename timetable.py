from typing import List, Tuple, Literal, Optional

import json
from courses import Course, Meeting, Selection
import sys
from constraints import Constraint
from datetime import time
from os import listdir
from os.path import isfile, join
from datetime import datetime

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
            ans += get_combinations([{
                "code": curr_course["code"],
                "term": term["term"],
                "meetings": [item]}
                for item in all_activities[0:1]], all_activities[1:])
        return ans

    def check_overlap_with_selection(self, prev: Selection, new_meeting: Meeting) -> bool:
        for meeting in prev["meetings"]:
            for time in meeting["times"]:
                if time["start"] == "None":  # Async timetable case
                    continue
                # datetime.
                for new_meeting_time in new_meeting["times"]:
                    if new_meeting_time["start"] == "None":  # Async timetable case
                        continue

    def check_overlap(self, term: str, meeting: Meeting) -> bool:
        time_periods: List[int] = []
        for time in meeting["times"]:
            if time["start"] == "None":  # Async timetable case
                return False
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
                raise Exception(f"Could not find day of week {meeting}")
            start_hour, start_minute = time["start"].split(":")
            end_hour, end_minute = time["end"].split(":")
            start = index + int(start_hour) * 2 + (start_minute == "30")
            end = index + int(end_hour) * 2 + (end_minute == "30")
            for i in range(start, end):
                if ((term in "FY" and self.timetable_first[i] is not None)
                        or (term in "SY" and self.timetable_second[i] is not None)):
                    return True
            return False


print(Timetable().get_possible_selections(0))
