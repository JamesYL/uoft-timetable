from typing import TypedDict, List, Optional, Literal, Dict, NewType
from datetime import time
import json
from courses import Course

CourseCode = NewType('CourseCode', str)
CommuteTime = NewType('CommuteTime', float)
Section = NewType("Section", str)           # Like LEC0101 or PRA0301
TermType = NewType("TermType", str)         # F, S, or Y


class CourseConstraint:
    term: TermType
    exclude: List[Section]

    def __init__(self, term: TermType, exclude: List[Section]):
        if term not in "FSY":
            raise Exception(
                f"Constraint error, term is not F, S, or Y. Term: {term} Exclude: {exclude}")
        self.term = term
        self.exclude = exclude

    def __str__(self):
        return f"Term: {term}, Exclude: {self.exclude}"


class Constraint:
    smallest_start_time: time
    biggest_end_time: time
    course_constraint: Dict[CourseCode, CourseConstraint]
    commute_time: CommuteTime

    def __init__(self, smallest_start_time: str, biggest_end_time: str, course_constraint: Dict[str, CourseConstraint], commute_time: float):
        self.smallest_start_time = time.fromisoformat(smallest_start_time)
        self.biggest_end_time = time.fromisoformat(biggest_end_time)
        self.course_constraint = course_constraint
        self.commute_time = commute_time/60


def parse_constraints_json() -> Constraint:
    with open("./constraints.json") as constraint_f:
        constraint_obj = json.load(constraint_f)
        course_constraint = {}
        for code in constraint_obj["course_constraint"]:
            course_constraint[code] = CourseConstraint(
                constraint_obj["course_constraint"][code]["term"],
                constraint_obj["course_constraint"][code]["exclude"])
        return Constraint(
            constraint_obj["smallest_start_time"],
            constraint_obj["biggest_end_time"],
            course_constraint,
            constraint_obj["commute_time"])


def filter_course(constraint: Constraint, course: Course) -> None:
    if course.code in constraint.course_constraint:
        course_constraint = constraint.course_constraint[course.code]

        included_term = None
        for term in course.terms:
            if term.term == course_constraint.term:
                included_term = term
        course.terms = []
        if included_term is not None:
            course.terms.append(included_term)
    for term in course.terms:
        for activity_type in term.meetings:
            new_meetings = []
            for meeting in term.meetings[activity_type]:
                bad_meeting = False
                for t in meeting.times:
                    if not t.is_sync:
                        continue
                    bad_meeting = t.working_hours[1] < constraint.smallest_start_time or t.working_hours[2] > constraint.biggest_end_time
                    if bad_meeting:
                        break
                if not bad_meeting:
                    new_meetings.append(meeting)
            term.meetings[activity_type] = new_meetings
