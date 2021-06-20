import fs from "fs";
import { simplifyCourses } from "../../src/simplify_data";
import path from "path";
import { getCourses } from "../../src/get_data";
import { sortCourses } from "../sort_helper";
const codeSimplified = simplifyCourses(
  getCourses(path.join(__dirname, "courses"))
);
const allSimplified = fs
  .readdirSync(path.join(__dirname, "simplified"))
  .map((file) =>
    JSON.parse(
      fs.readFileSync(path.join(__dirname, "simplified", file), "utf8")
    )
  );
sortCourses(codeSimplified);
sortCourses(allSimplified);
const compare = (code: string) => {
  const curr = codeSimplified.filter((item) => item.code === code);
  const curr2 = allSimplified.filter((item) => item.code === code);
  if (curr.length !== 1 || curr2.length !== 1) throw Error("Bad code");
  sortCourses(curr);
  sortCourses(curr2);
  expect(curr).toEqual(curr2);
};
describe("Two activities same term same activity type", () => {
  test("Two async", () => compare("async"));
  test("One async one sync", () => compare("async_sync"));
  test("Sync with all same except day", () => compare("sync_diff_day"));
  test("Sync with all same except end time", () => compare("sync_diff_end"));
  test("Sync with all same except start time", () =>
    compare("sync_diff_start"));
  test("Sync with all equal", () => compare("sync_equal"));
  test("Sync but one has more times", () => compare("sync_extra_time"));
});
test("Different courses", () => {
  expect(codeSimplified).toEqual(allSimplified);
});
test("Different activities", () => {
  compare("diff_activity");
});
describe("Different terms", () => {
  compare("diff_term");
});
