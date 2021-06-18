from typing import List, Tuple, Literal, Optional, NewType

import json
from courses import Course, Meeting, Time, Term, parse_courses_json, WorkingHours
import sys
from constraints import Constraint, filter_course
from datetime import time
from os import listdir
from os.path import isfile, join
from constraints import parse_constraints_json

TermType = NewType("TermType", str)  # F, S, or Y


class Selection:
    def __init__(self, code: str, term: TermType, meetings: List[Meeting]):
        self.code = code
        self.term = term
        self.meetings = meetings

    def __str__(self):
        return f"{self.code} {self.term} {[str(item) for item in self.meetings]}"


class FlattenedSelection:
    def __init__(self, code: str, term: TermType, instructors: List[str], space: str,
                 waitlist: str, notes: str, activity: str, working_hours: WorkingHours, is_sync: bool):
        self.code = code
        self.term = term
        self.instructors = instructors
        self.space = space
        self.waitlist = waitlist
        self.notes = notes
        self.working_hours = working_hours
        self.activity = activity
        self.is_sync = is_sync

    def __str__(self):
        if not self.is_sync:
            return f"{self.code}-{self.term} {self.activity} for {self.working_hours}"
        index_to_weekday = {1: "Monday", 2: "Tuesday",
                            3: "Wednesday", 4: "Thursday", 5: "Friday"}
        start_hour = str(self.working_hours[1].hour)
        if len(start_hour) == 1:
            start_hour = f"0{start_hour}"
        end_hour = str(self.working_hours[2].hour)
        if len(end_hour) == 1:
            end_hour = f"0{end_hour}"
        start_minute = str(self.working_hours[1].minute)
        if len(start_minute) == 1:
            start_minute = f"0{start_minute}"
        end_minute = str(self.working_hours[2].minute)
        if len(end_minute) == 1:
            end_minute = f"0{end_minute}"
        return f"{self.code}-{self.term} {self.activity} on {index_to_weekday[self.working_hours[0]]} from {start_hour}:{start_minute} to {end_hour}:{end_minute}"


class Timetable:
    def __init__(self):
        # Works by every half hour.
        # index 5 refers to the time period from 02:30 to 03:00
        self.timetable_first: List[Optional[Meeting]] = [None] * 24 * 2 * 5
        self.timetable_second: List[Optional[Meeting]] = [None] * 24 * 2 * 5

        self.constraint = parse_constraints_json()
        self.courses: List[Course] = parse_courses_json()
        for item in self.courses:
            filter_course(self.constraint, item)
            item.simplify()

    def time_to_index(self, t: Time) -> int:
        if not t.is_sync:
            return 0, 0
        index = 0
        working_hours: Tuple[int, time, time] = t.working_hours
        day, start, end = working_hours
        day_to_index = {1: 0, 2: 48, 3: 96, 4: 144, 5: 192}
        index = day_to_index[day]
        s = index + start.hour * 2 + (start.minute == 30)
        e = index + end.hour * 2 + (end.minute == 30)
        return s, e

    def add_to_timetable(self, selection: Selection):
        term = selection.term
        for meeting in selection.meetings:
            for time in meeting.times:
                start, end = self.time_to_index(time)
                for i in range(start, end):
                    if ((term in "FY" and self.timetable_first[i] is not None)
                            or (term in "SY" and self.timetable_second[i] is not None)):
                        raise Exception(
                            f"Trying to add to timetable when slot is used: {selection}")
                    if term in "FY":
                        self.timetable_first[i] = selection
                    if term in "SY":
                        self.timetable_second[i] = selection

    def remove_from_timetable(self, selection: Selection):
        term = selection.term
        for meeting in selection.meetings:
            for time in meeting.times:
                start, end = self.time_to_index(time)
                for i in range(start, end):
                    if ((term in "FY" and self.timetable_first[i] is None)
                            or (term in "SY" and self.timetable_second[i] is None)):
                        raise Exception(
                            f"Trying to removed from timetable when slot isn't used: {selection}")
                    if term in "FY":
                        self.timetable_first[i] = None
                    if term in "SY":
                        self.timetable_second[i] = None

    def check_overlap(self, term: TermType, meeting: Meeting) -> bool:
        time_periods: List[int] = []
        for time in meeting.times:
            if not time.is_sync:
                return False
            start, end = self.time_to_index(time)
            for i in range(start, end):
                if ((term in "FY" and self.timetable_first[i] is not None)
                        or (term in "SY" and self.timetable_second[i] is not None)):
                    return True
        return False

    def check_overlap_with_selection(self, prev: Selection, new_meeting: Meeting) -> bool:
        for meeting in prev.meetings:
            for time1 in meeting.times:
                if not time1.is_sync:
                    continue
                for time2 in new_meeting.times:
                    if not time2.is_sync:
                        continue
                    if (time1.working_hours[0] == time2.working_hours[0] and
                        time1.working_hours[1] < time2.working_hours[2] and
                            time1.working_hours[2] > time2.working_hours[1]):
                        return True
        return False

    def flatten_selection(self, selection: Selection) -> List[FlattenedSelection]:
        ans: List[FlattenedSelection] = []
        for meeting in selection.meetings:
            for t in meeting.times:
                ans.append(
                    FlattenedSelection(selection.code, selection.term,
                                       meeting.instructors, meeting.space, meeting.waitlist, meeting.notes,
                                       meeting.activity_type + meeting.activity_code, t.working_hours, t.is_sync))
        return ans

    def flatten_timetables(self, timetables: List[List[Selection]]) -> List[List[FlattenedSelection]]:
        flattened = []
        for list_of_selections in timetables:
            total = []
            for selection in list_of_selections:
                for item in self.flatten_selection(selection):
                    total.append(item)
            flattened.append(total)
        return flattened

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


    def get_combinations(self, so_far: List[Selection],
                         remaining: List[List[Meeting]]) -> List[Selection]:
        if len(remaining) == 0:
            return so_far
        new_so_far = []
        for item in so_far:
            for other in remaining[0]:
                if self.check_overlap_with_selection(item, other):
                    continue
                cpy = item.meetings[:]
                cpy.append(other)
                new_so_far.append(
                    Selection(item.code, item.term, cpy))
        return self.get_combinations(new_so_far, remaining[1:])

    def get_possible_selections(self, index: int) -> List[Selection]:
        curr_course = self.courses[index]
        ans: List[Selection] = []
        for term in curr_course.terms:
            all_activities: List[List[Meeting]] = []
            for activity_type in term.meetings:
                curr_activity_meetings: List[Meeting] = []
                for meeting in term.meetings[activity_type]:
                    if not self.check_overlap(term.term, meeting):
                        curr_activity_meetings.append(meeting)
                all_activities.append(curr_activity_meetings)
            if len(all_activities) > 0:
                ans += self.get_combinations([
                    Selection(curr_course.code, term.term, [m])
                    for m in all_activities[0]], all_activities[1:])
        return ans

    def display_nicely(self, selections: List[FlattenedSelection]) -> str:
        ans = []
        first = sorted(
            filter(lambda x: x.term in "FY", selections), key=self.sort_selection_comparator)
        second = sorted(
            filter(lambda x: x.term in "SY", selections), key=self.sort_selection_comparator)
        ans.append(
            "————————————————————————————————————————————— First Term —————————————————————————————————————————————")
        for s in first:
            ans.append(str(s))
        ans.append(
            "————————————————————————————————————————————— Second Term —————————————————————————————————————————————")
        for s in second:
            ans.append(str(s))
        ans.append("—————————————————————————————————————————————")
        return "\n".join(ans)

    def get_time(self, selections: List[FlattenedSelection]) -> int:
        # Assume selections is sorted by time
        total_time = 0
        visited_weekdays = set()
        for item in selections:
            if not item.is_sync:
                visited_weekdays.add(item.working_hours[0])
        total_time += self.constraint.commute_time * len(visited_weekdays)

        for i in range(len(selections) - 1):
            item = selections[i]
            item_after = selections[i+1]
            if not item.is_sync:
                break
            elif item.working_hours[0] == item_after.working_hours[0]:
                total_time += ((item_after.working_hours[1].hour * 60 +
                                item_after.working_hours[2].minute) -
                               (item.working_hours[1].hour * 60 +
                                item.working_hours[2].minute))
        return total_time

    def get_time_unsplit(self, selections: List[FlattenedSelection]) -> int:
        first_term = sorted(
            filter(lambda x: x.term in "FY", selections), key=self.sort_selection_comparator)
        second_term = sorted(
            filter(lambda x: x.term in "SY", selections), key=self.sort_selection_comparator)
        total_time = self.get_time(first_term) + self.get_time(second_term)
        return total_time

    def sort_selection_comparator(self, s: FlattenedSelection):
        if not s.is_sync:
            return (100, 100)
        return (s.working_hours[0], s.working_hours[1])

    def sort_by_wasted_time(self, items: List[List[FlattenedSelection]]) -> List[List[FlattenedSelection]]:
        def comparator(selections: List[FlattenedSelection]):
            return self.get_time(sorted(
                filter(lambda x: x.term in "FY", selections), key=self.sort_selection_comparator)) + self.get_time(sorted(
                    filter(lambda x: x.term in "SY", selections), key=self.sort_selection_comparator))
        return sorted(items, key=comparator)
