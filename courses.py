from typing import TypedDict, List, Optional, Literal, Dict, Union, Tuple, NewType
from typing import NewType
from datetime import time
from os import listdir
from os.path import isfile, join
import json

TermType = NewType("TermType", str)         # F, S, or Y
# 18:00 or 09:22 (must be 24 hour format)
TimeString = NewType("TimeString", str)
# Must be one of these, case in-sensitive ["monday", "tuesday""wednesday", "thursday", "friday"]
WeekDay = NewType("WeekDay", str)
ActivityType = NewType("ActivityType", str)  # Something like LEC, PRA, TUT
ActivityCode = NewType("ActivityCode", str)  # Something like 0101, 0202, 0304
WorkingHours = NewType("WorkingHours", Union[str, Tuple[int, time, time]])


class Time:
    is_sync: bool
    working_hours: WorkingHours

    def __init__(self, day_of_week: WeekDay, start=None, end=None):
        # day of week can also be instructions for async if start is None
        if not start:
            self.working_hours = day_of_week
            self.is_sync = False
        else:
            weekday_to_int = {
                "monday": 1,
                "tuesday": 2,
                "wednesday": 3,
                "thursday": 4,
                "friday": 5
            }
            self.is_sync = True
            self.working_hours = (weekday_to_int[day_of_week.lower()],
                                  time.fromisoformat(start), time.fromisoformat(end))

    def __str__(self):
        return str(self.working_hours)

    def __eq__(self, other):
        return self.is_sync == other.is_sync and self.working_hours == other.working_hours


class Meeting:
    instructors: List[str]
    space: str
    notes: str
    times: List[Time]
    activity_type: str
    activity_code: str

    def __init__(self, instructors: List[str], space: str, waitlist: str, notes: str, times: List[Time], activity_type: ActivityType, activity_code: ActivityCode):
        self.instructors = instructors
        self.space = space
        self.waitlist = waitlist
        self.notes = notes
        self.times = times
        self.activity_type = activity_type
        self.activity_code = activity_code

    def __str__(self):
        return f"{self.activity_type}{self.activity_code} {[str(item) for item in self.times]}"


class Term:
    term: TermType
    meetings: Dict[ActivityType, List[Meeting]]

    def __init__(self, term: TermType, meetings: Dict[ActivityType, List[Meeting]]):
        if term not in "FSY":
            raise Exception(
                f"Constraint error, term is not F, S, or Y. Term: {term} Meetings: {meetings}")
        self.term = term
        self.meetings = meetings

    def __str__(self):
        res = []
        for activity_type in self.meetings:
            tmp = []
            for meeting in self.meetings[activity_type]:
                tmp.append(str(meeting))
            res.append(tmp)
        return str(res)

    def simplify(self):
        for activity_type in self.meetings:
            self._simplify(activity_type)

    def _simplify(self, activity_type: ActivityType):
        meetings = self.meetings[activity_type]
        combined = []
        while len(meetings):
            same_time = [meetings.pop()]
            for i in range(len(meetings) - 1, -1, -1):
                curr = meetings[i]
                if curr.times == same_time[0].times:
                    same_time.append(curr)
                    meetings.pop(i)
            new_instructors = []
            for i, item in enumerate(same_time):
                for instructors in item.instructors:
                    new_instructors.append(instructors)
                if i != len(same_time) - 1:
                    new_instructors.append("/")
            new_space = "/".join([item.space for item in same_time])
            new_waitlist = "/".join([item.waitlist for item in same_time])
            new_notes = "/".join([item.notes for item in same_time])
            new_times = same_time[0].times
            new_activity_code = "/".join(
                [item.activity_code for item in same_time])
            combined.append(Meeting(new_instructors, new_space, new_waitlist, new_notes,
                                    same_time[0].times, same_time[0].activity_type, new_activity_code))
        self.meetings[activity_type] = combined


class Course:
    code: str
    terms: List[Term]

    def __init__(self, code: str, terms: List[Term]):
        self.code = code
        self.terms = terms

    def __str__(self):
        return str([str(item) for item in self.terms])

    def simplify(self):
        for item in self.terms:
            item.simplify()


def parse_courses_json() -> List[Course]:
    all_courses = []
    for f in listdir("courses"):
        loc = join("courses", f)
        if not isfile(loc):
            continue
        with open(loc) as course_file:
            course = json.load(course_file)
            code = course["code"]
            all_terms = []
            for term in course["terms"]:
                curr_term = term["term"]
                meetings_dict = {}
                for activity_type in term["meetings"]:
                    all_meetings = []
                    meetings = term["meetings"][activity_type]
                    for meeting in meetings:
                        all_times = []
                        for t in meeting["times"]:
                            if t["start"] is None:
                                all_times.append(Time(t["day_of_week"]))
                            else:
                                all_times.append(
                                    Time(t["day_of_week"], start=t["start"], end=t["end"]))
                        all_meetings.append(Meeting(meeting["instructors"], meeting["space"], meeting["waitlist"],
                                                    meeting["notes"], all_times, meeting["activity_type"], meeting["activity_code"]))
                    meetings_dict[activity_type] = all_meetings
                all_terms.append(Term(curr_term, meetings_dict))
            all_courses.append(Course(code, all_terms))
    return all_courses
