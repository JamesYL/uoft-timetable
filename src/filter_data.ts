import {
  Course,
  UpdatedExclude,
  FilteredConstraint,
  FilteredCourseConstraint,
  Meeting,
  Term,
} from "./get_data";
/**
 * Remove courses that don't comply with the constraints set
 * @param courses The courses
 * @param constraint The constraints
 * @returns Filtered courses
 */
export const filterData = (
  courses: Course[],
  constraint: FilteredConstraint
): Course[] => {
  courses.forEach((course) => filterCourse(course, constraint));
  return courses;
};
const filterCourse = (course: Course, constraint: FilteredConstraint) => {
  filterMeetingByTime(constraint.smallestTime, constraint.biggestTime, course);
  if (course.code in constraint.courseConstraint) {
    filterMeetingByCourseConstraint(
      course,
      constraint.courseConstraint[course.code]
    );
  }
};
const filterMeetingByCourseConstraint = (
  course: Course,
  courseConstraint: FilteredCourseConstraint
) => {
  const correctTerm = course.terms.filter(
    (term) => term.term === courseConstraint.term
  );
  if (correctTerm.length > 1) {
    throw Error(`Course has duplicate terms ${course}`);
  }
  course.terms = correctTerm;
  if (correctTerm.length === 1) {
    filterMeetingsByExclusions(correctTerm[0], courseConstraint.exclude);
  }
};
const filterMeetingsByExclusions = (term: Term, exclude: UpdatedExclude) => {
  for (const activityType in term.meetings) {
    const meetings = term.meetings[activityType];
    term.meetings[activityType] = meetings.filter((meeting) => {
      for (const item of exclude) {
        if (
          meeting.activityType === item[0] &&
          meeting.activityCode === item[1]
        )
          return false;
      }
      return true;
    });
  }
};
const filterMeetingByTime = (
  smallest: number,
  biggest: number,
  course: Course
) => {
  course.terms.forEach((term) => {
    for (const activityType in term.meetings) {
      const newMeetings: Meeting[] = [];
      for (const meeting of term.meetings[activityType]) {
        let isGood = true;
        for (const time of meeting.times) {
          if (time.instructions) continue;
          else if (time.start < smallest || time.end > biggest) {
            isGood = false;
            break;
          }
        }
        if (isGood) newMeetings.push(meeting);
      }
      term.meetings[activityType] = newMeetings;
    }
  });
};
