import { FlattenedMeeting } from "./get_timetables";
import fs from "fs";
import { flattenedMeetingComparator } from "./find_minimal_timetable";
/**
 * Displaying the minimal timetables in output file
 * @param meetings The timetables
 * @param minutesWasted Commute time used
 * @param maxPrint Max timetables displayed
 */
export const displayMeetings = (
  meetings: FlattenedMeeting[][],
  minutesWasted: number,
  maxPrint: number,
  outputLoc = "./output.txt"
): void => {
  if (meetings.length === 0)
    fs.writeFileSync(
      outputLoc,
      "No possible timetable can be generated with current constraints and courses"
    );
  else {
    const outputStrs: string[] = [];
    outputStrs.push(
      `Total of ${meetings.length} timetable(s) with minimal wasted time generated.`
    );
    outputStrs.push(
      `${minutesWasted / 60} hours wasted per week (both terms).`
    );
    for (let i = 0; i < Math.min(meetings.length, maxPrint); i++)
      outputStrs.push(displayTimetable(meetings[i]));
    fs.writeFileSync(outputLoc, outputStrs.join("\n"));
  }
  console.log("Successfully generated timetables");
};

const displayTimetable = (meetings: FlattenedMeeting[]) => {
  meetings.sort(flattenedMeetingComparator);
  const firstDivider = "—————————————————First Term—————————————————";
  const firstTerm = meetings
    .filter((meeting) => "FY".includes(meeting.term))
    .map(displayNice)
    .join("\n");
  const secondDivider = "—————————————————Second Term—————————————————";

  const secondTerm = meetings
    .filter((meeting) => "SY".includes(meeting.term))
    .map(displayNice)
    .join("\n");
  return `\n${firstDivider}\n${firstTerm}\n${secondDivider}\n${secondTerm}\n`;
};

const displayNice = (meeting: FlattenedMeeting) => {
  const allCodes = meeting.meetings.map((item) => item.activityCode).join("/");
  if (meeting.instructions) {
    return `${meeting.code}-${meeting.term} for ${meeting.instructions} on ${meeting.activityType}${allCodes}`;
  }
  const intToDay = { 1: "Mon", 2: "Tues", 3: "Wed", 4: "Thurs", 5: "Fri" };
  const startHour = `${~~(meeting.start / 60)}`;
  const startMin = `${meeting.start % 60}`;
  const startTime =
    `${startHour}:` + (startMin.length === 1 ? `0${startMin}` : startMin);
  const endHour = `${~~(meeting.end / 60)}`;
  const endMin = `${meeting.end % 60}`;
  const endTime = `${endHour}:` + (endMin.length === 1 ? `0${endMin}` : endMin);
  return `${meeting.code}-${meeting.term} on ${
    intToDay[meeting.dayOfWeek as 1 | 2 | 3 | 4 | 5]
  } from ${startTime} to ${endTime} for ${meeting.activityType}${allCodes}`;
};
