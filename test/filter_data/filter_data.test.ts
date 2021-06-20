import path from "path";
import { filterData } from "../../src/filter_data";
import { getConstraint, getCourses } from "../../src/get_data";

test("Filter data", () => {
  const courses = getCourses(path.join(__dirname, "courses"));
  const constraint = getConstraint(path.join(__dirname, "constraints.json"));
  const course1 = {
    code: "CSC209",
    terms: [
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
          TUT: [],
        },
      },
    ],
  };
  const course2 = {
    code: "CSC343",
    terms: [
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
        meetings: { LEC: [], TUT: [] },
      },
    ],
  };

  const items = [course1, course2];
  items.sort();
  const res = filterData(
    courses.filter((item) => item.code !== "CSC148"),
    constraint
  );
  res.sort();
  expect(res).toEqual(items);
  expect(() =>
    filterData(
      courses.filter((item) => item.code === "CSC148"),
      constraint
    )
  ).toThrow(/Course has duplicate terms.*/);
});
