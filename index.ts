import { getAllTimetables } from "./src/get_timetables";
import { getCourses, getConstraint } from "./src/get_data";
import { filterData } from "./src/filter_data";
import { simplifyCourses } from "./src/simplify_data";
import { findMinimalTimetable } from "./src/find_minimal_timetable";
import { displayMeetings } from "./src/display";
const constraint = getConstraint();
const courses = filterData(getCourses(), constraint); // Remove courses that don't comply with the constraints set
const simplifiedCourses = simplifyCourses(courses); // Combining activities in courses that have the same times
const allTimetables = getAllTimetables(simplifiedCourses); // All possible valid timetables

// Timetables that have minimal wasted time (commute time + time between courses)
const [minimalTimetables, minutesWasted] = findMinimalTimetable(
  constraint.commute,
  allTimetables
);
displayMeetings(minimalTimetables, minutesWasted, constraint.maxPrint); // Displaying the minimal timetables
