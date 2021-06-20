export type ActivityType = string;
export type ActivityCode = string;
export type UpdatedExclude = [ActivityType, ActivityCode][];
export type TermType = "F" | "S" | "Y";
export type CourseCode = string;
export interface Course {
  code: CourseCode;
  terms: Term[];
}
export interface Term {
  term: TermType;
  meetings: MeetingsByActivityType;
}
export interface MeetingsByActivityType {
  [activityType: string]: Meeting[];
}
export interface Meeting {
  instructors: string[];
  space: string;
  waitlist: string;
  notes: string;
  times: Time[];
  activityCode: ActivityCode;
  activityType: ActivityType;
}
export interface Time {
  dayOfWeek: 1 | 2 | 3 | 4 | 5;
  start: number;
  end: number;
  instructions: string;
}
interface Constraint {
  smallest_start_time: string;
  biggest_end_time: string;
  commute_time: number;
  course_constraint: {
    [key: string]: CourseConstraint;
  };
  print_amount: number;
}
interface CourseConstraint {
  term: TermType;
  exclude: string[];
}
export interface FilteredConstraint {
  smallestTime: number;
  biggestTime: number;
  commute: number;
  courseConstraint: {
    [key: string]: FilteredCourseConstraint;
  };
  maxPrint: number;
}
export interface FilteredCourseConstraint {
  term: TermType;
  exclude: UpdatedExclude;
}

import * as fs from "fs";
import path from "path";
const CONSTRAINTS_FILE_LOC = "./constraints.json";
const COURSES_DIR_LOC = "./courses";

/**
 * Get constraints
 * @param constraintsFile Location for constraints json file
 * @returns constraints
 */
export const getConstraint = (
  constraintsFile = CONSTRAINTS_FILE_LOC
): FilteredConstraint => {
  const constraints: Constraint = JSON.parse(
    fs.readFileSync(constraintsFile, "utf8")
  );
  const [startHour1, startMin1] = constraints.smallest_start_time.split(":");
  const [endHour1, endMin2] = constraints.biggest_end_time.split(":");
  const filteredCourseConstraints: {
    [key: string]: FilteredCourseConstraint;
  } = {};
  for (const key in constraints.course_constraint) {
    const curr = constraints.course_constraint[key];
    filteredCourseConstraints[key] = {
      term: curr.term,
      exclude: curr.exclude.map((item) => [
        item.substring(0, 3),
        item.substring(3),
      ]),
    };
  }

  const filteredConstraints: FilteredConstraint = {
    smallestTime: parseInt(startHour1) * 60 + parseInt(startMin1),
    biggestTime: parseInt(endHour1) * 60 + parseInt(endMin2),
    commute: constraints.commute_time,
    courseConstraint: filteredCourseConstraints,
    maxPrint: constraints.print_amount,
  };
  return filteredConstraints;
};
/**
 * All courses after parsing from json files
 * @param coursesDir Directory containing json files
 * @returns All courses
 */
export const getCourses = (coursesDir = COURSES_DIR_LOC): Course[] => {
  const courses: Course[] = fs
    .readdirSync(coursesDir)
    .map((file) =>
      JSON.parse(fs.readFileSync(path.join(coursesDir, file), "utf8"))
    );
  return courses;
};
