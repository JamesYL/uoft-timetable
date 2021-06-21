import { SimplifiedCourse, SimplifiedMeeting } from "./simplify_data";
import {
  addToTimetable,
  checkOverlap,
  createEmptyTimetable,
  FullTimetable,
  removeFromTimetable,
} from "./timetable";
import { ActivityType, CourseCode, Meeting, TermType } from "./get_data";

type Selection = SimplifiedMeeting[];
export interface FlattenedMeeting {
  activityType: ActivityType;
  term: TermType;
  code: CourseCode;
  dayOfWeek: 1 | 2 | 3 | 4 | 5;
  start: number;
  end: number;
  instructions: string;
  meetings: Meeting[];
}
/**
 * @param courses All courses
 * @returns All possible valid timetables
 */
export const getAllTimetables = (
  courses: SimplifiedCourse[]
): FlattenedMeeting[][] => {
  return getAllTimetablesHelper([], [], courses, createEmptyTimetable(), 0);
};
export const getAllTimetablesHelper = (
  past: FlattenedMeeting[],
  ans: FlattenedMeeting[][],
  courses: SimplifiedCourse[],
  timetable: FullTimetable,
  index: number
): FlattenedMeeting[][] => {
  if (index === courses.length) {
    if (index !== 0) {
      ans.push([...past]);
    }
  } else {
    const curr = getPossibleSelections(timetable, courses[index]);
    for (const selection of curr) {
      for (const meeting of selection) {
        meeting.times.forEach((time) =>
          past.push({
            activityType: meeting.activityType,
            term: meeting.term,
            code: meeting.code,
            dayOfWeek: time.dayOfWeek,
            start: time.start,
            end: time.end,
            instructions: time.instructions,
            meetings: meeting.meetings,
          })
        );
        addToTimetable(timetable, meeting);
      }
      getAllTimetablesHelper(past, ans, courses, timetable, index + 1);
      for (const meeting of selection) {
        meeting.times.forEach(() => past.pop());
        removeFromTimetable(timetable, meeting);
      }
    }
  }
  return ans;
};
const getPossibleSelections = (
  currTimetable: FullTimetable,
  course: SimplifiedCourse
): Selection[] => {
  const allPossible: Selection[] = [];
  for (const term of course.terms) {
    const allSimplifiedMeetings: SimplifiedMeeting[][] = [];
    for (const activityType in term.meetings) {
      const sameType: SimplifiedMeeting[] = [];
      for (const meeting of term.meetings[activityType]) {
        if (!checkOverlap(currTimetable, meeting)) sameType.push(meeting);
      }
      allSimplifiedMeetings.push(sameType);
    }
    getCombinations(allSimplifiedMeetings, [])
      .filter(isValidSelection)
      .forEach((s) => allPossible.push(s));
  }

  return allPossible;
};
const isValidSelection = (selection: Selection): boolean => {
  for (let i = 0; i < selection.length; i++) {
    for (let j = i + 1; j < selection.length; j++) {
      if (isSimplifiedMeetingOverlap(selection[i], selection[j])) {
        return false;
      }
    }
  }
  return true;
};
const isSimplifiedMeetingOverlap = (
  meeting1: SimplifiedMeeting,
  meeting2: SimplifiedMeeting
): boolean => {
  for (const time1 of meeting1.times) {
    if (time1.instructions) return false;
    for (const time2 of meeting2.times) {
      if (time2.instructions) return false;
      else if (
        time1.dayOfWeek === time2.dayOfWeek &&
        ((time1.start >= time2.start && time1.start < time2.end) ||
          (time1.end > time2.start && time1.end <= time2.end))
      )
        return true;
    }
  }
  return false;
};
const getCombinations = (
  meetings: SimplifiedMeeting[][],
  soFar: Selection[] = []
): Selection[] => {
  if (meetings.length === 0) return soFar;
  else if (soFar.length === 0)
    return getCombinations(
      meetings.slice(1),
      meetings[0].map((item) => [item])
    );
  const newSoFar: Selection[] = [];
  for (const item of soFar) {
    for (const other of meetings[0]) {
      const cpy = [...item, other];
      newSoFar.push(cpy);
    }
  }
  return getCombinations(meetings.slice(1), newSoFar);
};
