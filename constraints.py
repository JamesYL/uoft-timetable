from typing import TypedDict, List, Optional, Literal, Dict


class CourseConstraint(TypedDict):
    term: Literal["F", "S", "Y"]
    exclude: List[str]  # List of sections like: [LEC0101, PRA0301]


class Constraint(TypedDict):
    smallest_start_time: str
    biggest_end_time: str
    course_constraint: Dict[str, CourseConstraint]
    commute_time: int  # in minutes (both ways)
