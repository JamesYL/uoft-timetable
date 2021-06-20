import {
  Time,
  Meeting,
  Course,
  MeetingsByActivityType,
  Term,
  TermType,
  ActivityType,
  CourseCode,
} from "./get_data";
export interface SimplifiedMeeting {
  activityType: ActivityType;
  term: TermType;
  code: CourseCode;
  times: Time[];
  meetings: Meeting[];
}
export interface SimplifiedCourse {
  code: string;
  terms: SimplifiedTerm[];
}
export interface SimplifiedTerm {
  term: "F" | "S" | "Y";
  meetings: SimplifiedMeetingsByActivityType;
}
export interface SimplifiedMeetingsByActivityType {
  [activityType: string]: SimplifiedMeeting[];
}
/**
 * Combining activities in courses that have the same times
 * @param courses All courses
 * @returns Courses but activities with same times are combined
 */
export const simplifyCourses = (courses: Course[]): SimplifiedCourse[] =>
  courses.map((item) => simplifyCourse(item));

const simplifyCourse = (course: Course): SimplifiedCourse => ({
  code: course.code,
  terms: course.terms.map((term) => simplifyTerm(term, course.code)),
});

const simplifyTerm = (term: Term, code: CourseCode): SimplifiedTerm => {
  return {
    term: term.term,
    meetings: simplifyMeetingsAllActivity(term.meetings, term.term, code),
  };
};

const simplifyMeetingsAllActivity = (
  meetings: MeetingsByActivityType,
  term: TermType,
  code: CourseCode
): SimplifiedMeetingsByActivityType => {
  const simplifiedByActivityType: SimplifiedMeetingsByActivityType = {};
  for (const activityType in meetings) {
    simplifiedByActivityType[activityType] = simplifyMeetingsSameActivity(
      meetings[activityType],
      term,
      code
    );
  }
  return simplifiedByActivityType;
};
const simplifyMeetingsSameActivity = (
  meetings: Meeting[],
  term: TermType,
  code: CourseCode
): SimplifiedMeeting[] => {
  const combined: SimplifiedMeeting[] = [];

  while (meetings.length) {
    const goodMeetings: Meeting[] = [meetings.pop() as Meeting];
    const badMeetings: Meeting[] = [];
    for (let i = 0; i < meetings.length; i++) {
      if (sameTime(goodMeetings[0].times, meetings[i].times)) {
        goodMeetings.push(meetings[i]);
      } else {
        badMeetings.push(meetings[i]);
      }
      meetings = badMeetings;
    }
    combined.push({
      activityType: goodMeetings[0].activityType,
      times: goodMeetings[0].times,
      meetings: goodMeetings,
      code,
      term,
    });
  }
  return combined;
};
const sameTime = (time: Time[], otherTime: Time[]): boolean => {
  if (time.length !== otherTime.length) return false;
  const comparator = (a: Time, b: Time) => {
    if (a.instructions && b.instructions) {
      if (a.dayOfWeek < b.dayOfWeek) return -1;
      else if (b.dayOfWeek < a.dayOfWeek) return 1;
      else if (a.start < b.start) return -1;
      return 1;
    } else if (a.instructions) return 1;
    else if (b.instructions) return -1;
    else if (a.dayOfWeek < b.dayOfWeek) return -1;
    else if (b.dayOfWeek < a.dayOfWeek) return 1;
    else if (a.start < b.start) return -1;
    return 1;
  };
  time.sort(comparator);
  otherTime.sort(comparator);
  for (let i = 0; i < time.length; i++) {
    if (
      (!!time[i].instructions && !otherTime[i].instructions) ||
      (!time[i].instructions && !!otherTime[i].instructions)
    )
      return false; // One is async but the other one isn't

    // If both aren't async and different stuff
    if (
      !time[i].instructions &&
      !otherTime[i].instructions &&
      (time[i].dayOfWeek !== otherTime[i].dayOfWeek ||
        time[i].start !== otherTime[i].start ||
        time[i].end !== otherTime[i].end)
    )
      return false;
  }

  return true;
};
