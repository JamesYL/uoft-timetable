from typing import TypedDict, List, Optional, Literal, Dict
from typing import NewType


class Time(TypedDict):
    day_of_week: str  # If async meeting, will show hours per week instead
    start: str  # None if async meeting
    end: str  # None if async meeting


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


class Selection(TypedDict):
    code: str
    term: Literal["F", "S", "Y"]
    meetings: List[Meeting]

class FlattenedSelection(TypedDict):
    code: str
    term: Literal["F", "S", "Y"]
    instructors: List[str]
    space: str
    waitlist: str
    notes: str
    day_of_week: str  # If async meeting, will show hours per week instead
    start: str  # None if async meeting
    end: str  # None if async meeting
    activity: str