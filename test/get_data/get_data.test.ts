import path from "path";
import { getConstraint, getCourses, Term } from "../../src/get_data";

describe("Getting data", () => {
  test("Get courses", () => {
    const courses = getCourses(path.join(__dirname, "courses"));
    const terms: Term[] = [
      {
        term: "S",
        meetings: {
          TUT: [
            {
              instructors: [],
              space: "17 of 156 available",
              waitlist: "No",
              notes: "",
              times: [
                {
                  instructions: "Asynchronous (See Delivery Instructions.)",
                  start: 0,
                  end: 0,
                  dayOfWeek: 1,
                },
              ],
              activityType: "TUT",
              activityCode: "0401",
            },
          ],
        },
      },
      {
        term: "F",
        meetings: {
          LEC: [
            {
              instructors: ["Reid, K."],
              space: "21 of 140 available",
              waitlist: "Yes: 0 student",
              notes: "Online - Synchronous (See Delivery Instructions.)",
              times: [
                { instructions: "", start: 1080, end: 1200, dayOfWeek: 2 },
              ],
              activityType: "LEC",
              activityCode: "5101",
            },
          ],
          TUT: [
            {
              instructors: [],
              space: "17 of 156 available",
              waitlist: "No",
              notes: "",
              times: [
                {
                  instructions: "Asynchronous (See Delivery Instructions.)",
                  start: 0,
                  end: 0,
                  dayOfWeek: 1,
                },
              ],
              activityType: "TUT",
              activityCode: "0401",
            },
          ],
        },
      },
    ];
    for (const course of courses) {
      expect({ code: course.code, terms }).toEqual(course);
    }
  });
  test("Get constraints", () => {
    const constraint = getConstraint(path.join(__dirname, "constraints.json"));
    const realConstraints = {
      smallestTime: 540,
      biggestTime: 1260,
      commute: 120,
      courseConstraint: {
        ANT100: {
          term: "Y",
          exclude: [
            ["LEC", "5109"],
            ["LEC", "0202"],
          ],
        },
        MAT137: {
          term: "S",
          exclude: [
            ["LEC", "5104"],
            ["LEC", "1002"],
          ],
        },
      },
      maxPrint: 5,
    };
    expect(constraint).toEqual(realConstraints);
  });
});
