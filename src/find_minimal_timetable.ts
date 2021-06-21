import { FlattenedMeeting } from "./get_timetables";
/**
 * Find timetables that minimze commute time and time wasted between classes
 * @param commute Commute time both ways
 * @param allMeetings Timetables being computed
 * @returns The minimal timetables
 */
export const findMinimalTimetable = (
  commute: number,
  allMeetings: FlattenedMeeting[][]
): [FlattenedMeeting[][], number] => {
  const commuteTimeToMeetings: {
    [time: number]: FlattenedMeeting[][];
  } = {};
  let smallest = 1000000;
  for (const meetings of allMeetings) {
    const time = getCommuteTime(commute, meetings);
    if (!(time in commuteTimeToMeetings)) commuteTimeToMeetings[time] = [];
    commuteTimeToMeetings[time].push(meetings);
    if (time < smallest) smallest = time;
  }
  if (smallest === 1000000) return [[], smallest];
  return [commuteTimeToMeetings[smallest], smallest];
};
export const flattenedMeetingComparator = (
  a: FlattenedMeeting,
  b: FlattenedMeeting
): number => {
  if (a.instructions) return 1;
  else if (b.instructions) return -1;
  else if (a.dayOfWeek < b.dayOfWeek) return -1;
  else if (a.dayOfWeek > b.dayOfWeek) return 1;
  else if (a.start < b.start) return -1;
  else if (a.start > b.start) return 1;
  throw Error("Duplicate meeting at same time");
};
const getCommuteTime = (
  commute: number,
  meetings: FlattenedMeeting[]
): number => {
  const firstTerm = meetings.filter((meeting) => "FY".includes(meeting.term));
  const secondTerm = meetings.filter((meeting) => "SY".includes(meeting.term));

  firstTerm.sort(flattenedMeetingComparator);
  secondTerm.sort(flattenedMeetingComparator);
  return (
    commuteTimeHelper(commute, firstTerm) +
    commuteTimeHelper(commute, secondTerm)
  );
};
/**
 * Assumes meetings are sorted by time and everything is on the same term
 */
const commuteTimeHelper = (
  commute: number,
  meetings: FlattenedMeeting[]
): number => {
  const allDays = new Set<number>();
  for (let i = 0; i < meetings.length; i++) {
    if (meetings[i].instructions) break;
    allDays.add(meetings[i].dayOfWeek);
  }
  let total = allDays.size * commute;
  for (let i = 0; i < meetings.length; i++) {
    if (meetings[i].instructions) return total;
    else if (
      i + 1 !== meetings.length &&
      !meetings[i + 1].instructions &&
      meetings[i].dayOfWeek === meetings[i + 1].dayOfWeek
    ) {
      total += meetings[i + 1].start - meetings[i].end;
    }
  }
  return total;
};
