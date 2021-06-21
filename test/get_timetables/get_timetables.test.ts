import { getAllTimetables } from "./../../src/get_timetables";
// import { simplifyCourses } from "../../src/simplify_data";
import path from "path";
import { getCourses } from "../../src/get_data";
import { simplifyCourses } from "../../src/simplify_data";

describe("Getting timetables", () => {
  test("No conflicts", () => {
    const codeSimplified = simplifyCourses(
      getCourses(path.join(__dirname, "courses", "no_conflict"))
    );
    const timetables = getAllTimetables(codeSimplified);
    expect(timetables.length).toBe(5);
  });
});
