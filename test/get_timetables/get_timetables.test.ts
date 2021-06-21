import { getAllTimetables } from "./../../src/get_timetables";
import path from "path";
import { getCourses } from "../../src/get_data";
import { simplifyCourses } from "../../src/simplify_data";

describe("Getting timetables", () => {
  test("General", () => {
    const codeSimplified = simplifyCourses(
      getCourses(path.join(__dirname, "courses", "general"))
    );
    const timetables = getAllTimetables(codeSimplified);
    expect(timetables.length).toBe(60);
  });
  test("Consecutive meetings", () => {
    const codeSimplified = simplifyCourses(
      getCourses(path.join(__dirname, "courses", "consecutive"))
    );
    const timetables = getAllTimetables(codeSimplified);
    expect(timetables.length).toBe(2);
  });
  test("Conflict with time completely contained", () => {
    const codeSimplified = simplifyCourses(
      getCourses(path.join(__dirname, "courses", "conflict_contained"))
    );
    const timetables = getAllTimetables(codeSimplified);
    expect(timetables.length).toBe(0);
  });
  test("Conflict with time partially contained", () => {
    const codeSimplified = simplifyCourses(
      getCourses(
        path.join(__dirname, "courses", "conflict_partially_contained")
      )
    );
    const timetables = getAllTimetables(codeSimplified);
    expect(timetables.length).toBe(0);
  });
  test("Timetable but one selection has a conflict", () => {
    const codeSimplified = simplifyCourses(
      getCourses(path.join(__dirname, "courses", "selection_conflict"))
    );
    const timetables = getAllTimetables(codeSimplified);
    expect(timetables.length).toBe(1);
  });
  test("Empty case", () => {
    const codeSimplified = simplifyCourses(
      getCourses(path.join(__dirname, "courses", "no_courses"))
    );
    const timetables = getAllTimetables(codeSimplified);
    expect(timetables.length).toBe(0);
  });
});
