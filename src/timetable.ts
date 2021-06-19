import { Time } from "./get_data";
import { SimplifiedMeeting } from "./simplify_data";
type timetable = (SimplifiedMeeting | null)[];
export interface FullTimetable {
  first: timetable;
  second: timetable;
}

const timeToIndex = (t: Time): [number, number] => {
  if (t.instructions) return [0, 0];
  const dayToIndex = { 1: 0, 2: 48, 3: 96, 4: 144, 5: 192 };
  const startI = dayToIndex[t.dayOfWeek] + t.start / 30;
  const endI = dayToIndex[t.dayOfWeek] + t.end / 30;
  return [startI, endI];
};
export const createEmptyTimetable = (): FullTimetable => {
  // 24 hours per day * 2 (two half hours) * 5 (five days per week)
  return {
    first: Array(24 * 2 * 5).fill(null),
    second: Array(24 * 2 * 5).fill(null),
  };
};
export const addToTimetable = (
  timetable: FullTimetable,
  simplifiedMeeting: SimplifiedMeeting
): void => {
  for (const time of simplifiedMeeting.times) {
    const [startI, endI] = timeToIndex(time);
    for (let i = startI; i < endI; i++) {
      if (
        ("FY".includes(simplifiedMeeting.term) && timetable.first[i] != null) ||
        ("SY".includes(simplifiedMeeting.term) && timetable.second[i] != null)
      ) {
        throw new Error(
          `Trying to add to timetable when slot is used ${simplifiedMeeting}`
        );
      }
      if ("FY".includes(simplifiedMeeting.term))
        timetable.first[i] = simplifiedMeeting;
      if ("SY".includes(simplifiedMeeting.term))
        timetable.second[i] = simplifiedMeeting;
    }
  }
};
export const removeFromTimetable = (
  timetable: FullTimetable,
  simplifiedMeeting: SimplifiedMeeting
): void => {
  for (const time of simplifiedMeeting.times) {
    const [startI, endI] = timeToIndex(time);
    for (let i = startI; i < endI; i++) {
      if (
        ("FY".includes(simplifiedMeeting.term) &&
          timetable.first[i] === null) ||
        ("SY".includes(simplifiedMeeting.term) && timetable.second[i] === null)
      ) {
        throw new Error(
          `Trying to remove from timetable when slot is empty ${simplifiedMeeting}`
        );
      }
      if ("FY".includes(simplifiedMeeting.term)) timetable.first[i] = null;
      if ("SY".includes(simplifiedMeeting.term)) timetable.second[i] = null;
    }
  }
};
export const checkOverlap = (
  timetable: FullTimetable,
  meeting: SimplifiedMeeting
): boolean => {
  for (const time of meeting.times) {
    const [start, end] = timeToIndex(time);
    for (let i = start; i < end; i++) {
      if (
        ("FY".includes(meeting.term) && timetable.first[i] != null) ||
        ("SY".includes(meeting.term) && timetable.second[i] != null)
      )
        return true;
    }
  }
  return false;
};
