import fs from "fs";
import path from "path";
import { filterData } from "../../src/filter_data";
import { Course, getConstraint, getCourses } from "../../src/get_data";
const constraint = getConstraint(path.join(__dirname, "constraints.json"));

const correctFiltered: Course[] = fs
  .readdirSync(path.join(__dirname, "filtered"))
  .map((file) =>
    JSON.parse(fs.readFileSync(path.join(__dirname, "filtered", file), "utf8"))
  );
describe("Filtering data", () => {
  test("Excluding by time", () => {
    const code = "excluding_by_time";
    const codeCourses = filterData(
      getCourses(path.join(__dirname, "courses")).filter(
        (item) => item.code === code
      ),
      constraint
    );
    const actualCourses = correctFiltered.filter((item) => item.code === code);
    expect(codeCourses).toEqual(actualCourses);
  });
  test("Excluding by course", () => {
    const code = "excluding_course";
    const codeCourses = filterData(
      getCourses(path.join(__dirname, "courses")).filter(
        (item) => item.code === code
      ),
      constraint
    );
    const actualCourses = correctFiltered.filter((item) => item.code === code);
    expect(codeCourses).toEqual(actualCourses);
  });
  test("Duplicate term", () => {
    const code = "duplicate_term";
    expect(() =>
      filterData(
        getCourses(path.join(__dirname, "courses")).filter(
          (item) => item.code === code
        ),
        constraint
      )
    ).toThrow(/Course has duplicate terms .*/);
  });
  test("Excluding all terms", () => {
    const code = "exclude_all_terms";
    const codeCourses = filterData(
      getCourses(path.join(__dirname, "courses")).filter(
        (item) => item.code === code
      ),
      constraint
    );
    const actualCourses = correctFiltered.filter((item) => item.code === code);
    expect(codeCourses).toEqual(actualCourses);
  });
});
