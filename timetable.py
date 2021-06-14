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
        curr_course = self.courses[index]
        for term in curr_course["terms"]:
            all_activities = []
            for activity_code in term["meetings"]:
                curr_activity_meetings = []
                for meeting in term["meetings"][activity_code]:
                    if not self.check_overlap(term, meeting):
                        curr_activity_meetings.append(meeting)
                all_activities.append(curr_activity_meetings)

        return all_activities

    def check_overlap(self, term: str, meeting: Meeting) -> bool:
        time_periods: List[int] = []
        for time in meeting["times"]:
            if time["start"] == "None":  # Async timetable case
                return False
            datetime.time(time["start"])
            datetime.time(time["end"])

        if term == "F":
            for time in meeting["times"]:
                return False
            self.timetable_first[meeting.times]


print(Timetable().get_possible_selections(0))
