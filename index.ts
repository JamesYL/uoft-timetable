import { getAllTimetables } from "./src/get_timetables";
import { getCourses, getConstraint } from "./src/get_data";
import { filterData } from "./src/filter_data";
import { simplifyCourses } from "./src/simplify_data";
import { findMinimalTimetable } from "./src/find_minimal_timetable";
import { displayMeetings } from "./src/display";
const constraint = getConstraint("./constraints.json");
const courses = filterData(getCourses("./courses"), constraint);
const simplifiedCourses = simplifyCourses(courses);
const allTimetables = getAllTimetables(simplifiedCourses);
const [minimalTimetables, minutesWasted] = findMinimalTimetable(
  constraint.commute,
  allTimetables
);
displayMeetings(minimalTimetables, minutesWasted, constraint.maxPrint);

