from typing import TypedDict, List, Optional, Literal, Dict


class Time(TypedDict):
    day_of_week: str
    start: str
    end: str


class Meeting(TypedDict):
    instructors: str
    space: str
    waitlist: str
    notes: str
    times: List[Time]
    activity_type: str
    activity_code: str


class Term(TypedDict):
    term: Literal["F", "S", "Y"]
    meetings: Dict[str, List[Meeting]]  # key is the activity_type


class Course(TypedDict):
    code: str
    terms: List[Term]
