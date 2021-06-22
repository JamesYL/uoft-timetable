# Minimal Timetable for UTSG ArtSci

## What is it

Easily find a timetable that minimizes wasted time (commute time and time between classes) for UTSG ArtSci courses

## How to Start

1. Clone this project.
2. Run `npm install`.
3. Go to ArtSci's [timetable](https://timetable.iit.artsci.utoronto.ca/) with Chrome.
4. Enter in a course code and search for courses. The course code should be exact like `MAT137`, **NOT** `MAT` and **NOT** `MAT137H1-F`. **Don't** add any other filters either.
5. Open console by pressing `F12` (`Command + Option + J` for MacOS) and copy paste the code in `get_courses_script.js` into console. If Chrome asks you for permission for downloading, accept it. This script only works for ArtSci's timetable.
6. You should see a `{course-code}.json` file downloaded such as `MAT137.json`.
7. Repeat steps 4 - 6 for all the courses that you want.
8. Drag all the `.json` files into `./courses` in the project directory. Make sure there aren't any duplicates or any unwanted courses.
9. Setup your constraints, instructions [here](#constraints).
10. Run `npm start`. Look at `./output.txt` for generated timetables.

If after step 10 and no output at all is showing up, it's probably because it is calculating too many possibilities (this can be something like 100¹⁰ possibilities). To prevent this issue, make better [constraints](#constraints).

## Constraints

Constraints fix issues by reducing the number of possible timetables. For example, if a course must be in first term and not second term, setting a constraint for that is necessary. To do so, edit the `./constraints.json` file. Ensure the syntax is correct.

```json
{
  "smallest_start_time": "09:00",
  "biggest_end_time": "21:00",
  "course_constraint": {
    "BIO130": {
      "term": "F",
      "exclude": ["LEC0101", "TUT0304", "PRA0202", "LEC0202"]
    },
    "ECO101": {
      "term": "S",
      "exclude": []
    }
  },
  "commute_time": 120
}
```

### Global constraints

**`smallest_start_time`**: Earliest start time a course can be. It must follow a 24 hour time format of `mm:ss`. In this example, the earliest start time for a course is 9:00 am.

**`biggest_end_time`**: Latest end time a course can be. Same format as before. Example is the latest time for a course is 9:00 pm.

**`course_constraint`**: Each key must be a valid course code mentioned in step 4 of [How to Start](#how-to-start). The key must refer to an object with properties found [here](#constraints-for-courses). This key is **optional**! If there are no constraints a course, do not have the key for it.

**`commute_time`**: Total commute time each day in minutes (both ways)

### Constraints for Courses

**`term`**: Either `F`, `S`, or `Y` (First term, second term, both terms respectively). This forces the course to be in that specific term.

**`exclude`**: Exclude certain activites for the course. This means the timetable will not contain these sections. Each activity section must follow the exact format as shown in the ArtSci timetable. This means `{activity type}{activity code}` -> `LEC0101`. If there are no exclusions, leave it as an empty array `[]`.

## Notes

Try to add as many course constraints as possible.

- Some courses must be taken in first term or must be taken in second term due to prerequsites/corequsuites/exclusions, but offered in both terms
- Maybe exclude sections due to no priority, no space, bad instructors, delivery method, bad time

The program automatically combines sections that have the same type and same time already, so you don't have to exclude "duplicate" sections.

By adding more constraints, the "time wasted" increases since the program is designed to find a timetable that minimizes commute time and time spent between classes.

If the program takes too long to load, you will be forced to add more constraints since that reduces the number of possibilities to consider.

## Requirements

- [Node](https://nodejs.org/en/download/)
- Chrome (No guarantees for other browsers)
