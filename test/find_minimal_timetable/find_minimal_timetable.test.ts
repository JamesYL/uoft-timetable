import { FlattenedMeeting } from "./../../src/get_timetables";
import { findMinimalTimetable } from "../../src/find_minimal_timetable";
import { TermType } from "../../src/get_data";

const generateFlattenedMeeting = (
  dayOfWeek: 1 | 2 | 3 | 4 | 5,
  start: number,
  end: number,
  term: TermType,
  instructions = ""
): FlattenedMeeting => {
  return {
    activityType: "LEC",
    term,
    code: "123",
    dayOfWeek,
    start,
    end,
    instructions,
    meetings: [],
  };
};
describe("Find minimal timetable", () => {
  test("Correct wasted time", () => {
    const allMeetings = [
      [
        generateFlattenedMeeting(1, 690, 720, "F"),
        generateFlattenedMeeting(1, 570, 690, "F"),
        generateFlattenedMeeting(5, 570, 690, "F"),
        generateFlattenedMeeting(5, 690, 720, "S"),
        generateFlattenedMeeting(1, 780, 810, "F"),
        generateFlattenedMeeting(3, 780, 810, "F"),
        generateFlattenedMeeting(3, 570, 690, "F"),
        generateFlattenedMeeting(1, 1080, 1230, "F"),
      ],
    ];
    // 3 * 40 total commute, 60 + 270 for day 1, 90 for day 3 (F)
    // 1 * 40 total commute (S)
    expect(findMinimalTimetable(40, allMeetings)[1]).toEqual(580);
  });
  test("Correct minimal no async", () => {
    const correct1 = [
      generateFlattenedMeeting(1, 720, 750, "F"),
      generateFlattenedMeeting(1, 570, 690, "F"),
    ];
    const correct2 = [
      generateFlattenedMeeting(1, 720, 750, "S"),
      generateFlattenedMeeting(1, 570, 690, "S"),
    ];
    const allMeetings = [
      correct1,
      [
        generateFlattenedMeeting(1, 720, 750, "F"),
        generateFlattenedMeeting(3, 720, 750, "F"),
        generateFlattenedMeeting(1, 570, 690, "F"),
      ],
      correct2,
    ];
    expect(findMinimalTimetable(40, allMeetings)[0]).toEqual([
      correct1,
      correct2,
    ]);
  });
  test("Correct minimal with async", () => {
    const correct1 = [
      generateFlattenedMeeting(1, 570, 690, "F", "async"),
      generateFlattenedMeeting(1, 720, 750, "F", "async"),
      generateFlattenedMeeting(3, 720, 750, "F"),
    ];

    const allMeetings = [
      [
        generateFlattenedMeeting(1, 570, 690, "F"),
        generateFlattenedMeeting(1, 720, 750, "F"),
      ],
      correct1,
      [
        generateFlattenedMeeting(1, 570, 690, "S"),
        generateFlattenedMeeting(1, 720, 750, "S"),
      ],
    ];
    expect(findMinimalTimetable(40, allMeetings)[0]).toEqual([correct1]);
  });
  test("Empty case", () => {
    expect(findMinimalTimetable(40, [])[0]).toEqual([]);
  });
});
