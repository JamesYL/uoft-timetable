import { SimplifiedMeeting } from "./../src/simplify_data";
import { Meeting, Time } from "../src/get_data";
import { SimplifiedCourse, SimplifiedTerm } from "../src/simplify_data";

const courseComparator = (a: SimplifiedCourse, b: SimplifiedCourse) =>
  a.code < b.code ? -1 : a.code === b.code ? 0 : 1;
const termComparator = (a: SimplifiedTerm, b: SimplifiedTerm) =>
  a.term < b.term ? -1 : a.term === b.term ? 0 : 1;
const timeComparator = (a: Time, b: Time) => {
  if (a.instructions && b.instructions) {
    if (a.dayOfWeek < b.dayOfWeek) return -1;
    else if (b.dayOfWeek < a.dayOfWeek) return 1;
    else if (a.start < b.start) return -1;
    else if (a.start === b.start) return 0;
    return 1;
  } else if (a.instructions) return 1;
  else if (b.instructions) return -1;
  else if (a.dayOfWeek < b.dayOfWeek) return -1;
  else if (b.dayOfWeek < a.dayOfWeek) return 1;
  else if (a.start < b.start) return -1;
  else if (a.start === b.start) return 0;
  return 1;
};
const meetingComparator = (a: Meeting, b: Meeting) =>
  a.activityCode <= b.activityCode ? -1 : 1;
const simplifiedMeetingComparator = (
  a: SimplifiedMeeting,
  b: SimplifiedMeeting
) => {
  if (a.meetings.length === 0) return 1;
  else if (b.meetings.length === 0) return -1;
  return meetingComparator(a.meetings[0], b.meetings[0]);
};
export const sortCourses = (items: SimplifiedCourse[]): void => {
  items.sort(courseComparator);
  for (const course of items) sortOneCourse(course);
};
const sortOneCourse = (course: SimplifiedCourse): void => {
  course.terms.sort(termComparator);
  for (const term of course.terms) {
    for (const type in term.meetings) {
      const curr = term.meetings[type];
      for (const simplifiedMeeting of curr) {
        simplifiedMeeting.times.sort(timeComparator);
        for (const meeting of simplifiedMeeting.meetings) {
          meeting.times.sort(timeComparator);
        }
        simplifiedMeeting.meetings.sort(meetingComparator);
      }
      curr.sort(simplifiedMeetingComparator);
    }
  }
};
