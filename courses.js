let res = { code: null, terms: [] };
for (const course of document.querySelectorAll(".perCourse")) {
  const courseTitle = course.querySelector(".hiCC").innerText;
  const meetings = {};
  for (const meeting of course.querySelectorAll(".perMeeting")) {
    const activity = meeting.querySelector(".colCode").innerText;
    const days = [];
    for (const day of meeting.querySelectorAll(".colTime .colDay")) {
      const times = {};
      times.day_of_week = day.querySelector(".weekDay").innerText;
      const startAndEndTimes = day.querySelectorAll("time");
      if (startAndEndTimes.length == 0) {
        times.start = "None";
        times.end = "None";
      } else {
        times.start = startAndEndTimes[0].innerText;
        times.end = startAndEndTimes[1].innerText;
      }
      days.push(times);
    }
    const currMeeting = {};
    currMeeting.instructors = meeting.querySelector(".colInst").innerText;
    if (currMeeting.instructors.trim() === "—") currMeeting.instructors = "";
    currMeeting.space = meeting.querySelector(".colAvail").innerText;
    currMeeting.waitlist = meeting.querySelector(".colWait").innerText;
    currMeeting.notes = meeting.querySelector(".colNotes").innerText;
    currMeeting.times = days;
    currMeeting.activity_type = activity.substring(0, 3);
    currMeeting.activity_code = activity.substring(3);
    if (!(currMeeting.activity_type in meetings)) {
      meetings[currMeeting.activity_type] = [];
    }
    meetings[currMeeting.activity_type].push(currMeeting);
  }
  const code = courseTitle.substring(0, 6);
  const term = courseTitle.charAt(courseTitle.length - 1);
  if (!res.code) res.code = code;
  if (code == res.code) res.terms.push({ term, meetings });
}
if (res.code) {
  const element = document.createElement("a");
  element.setAttribute(
    "href",
    "data:text/plain;charset=utf-8," + encodeURIComponent(JSON.stringify(res))
  );
  element.setAttribute("download", `${res.code}.json`);
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}
