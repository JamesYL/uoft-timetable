let res = { code: null, terms: [] };
for (const course of document.querySelectorAll(".perCourse")) {
	const courseTitle = course.querySelector(".hiCC").innerText;
	const meetings = {};
	for (const meeting of course.querySelectorAll(".perMeeting")) {
		const activity = meeting.querySelector(".colCode").innerText;
		const days = [];
		for (const day of meeting.querySelectorAll(".colTime .colDay")) {
			const times = {};
			const startAndEndTimes = day.querySelectorAll("time");
			times.instructions = "";
			times.start = 0;
			times.end = 0;
			times.dayOfWeek = -1;
			if (startAndEndTimes.length == 0) {
				times.instructions = day.querySelector(".weekDay").innerText;
			} else {
				[startHour, startMin] = startAndEndTimes[0].innerText.split(":");
				[endHour, endMin] = startAndEndTimes[1].innerText.split(":");
				dayToInt = {
					monday: 1,
					tuesday: 2,
					wednesday: 3,
					thursday: 4,
					friday: 5,
				};
				times.dayOfWeek =
          dayToInt[day.querySelector(".weekDay").innerText.toLowerCase()];
				times.start = parseInt(startHour) * 60 + parseInt(startMin);
				times.end = parseInt(endHour) * 60 + parseInt(endMin);
			}
			days.push(times);
		}
		const currMeeting = {};
		currMeeting.instructors = meeting.querySelector(".colInst").innerText;
		if (currMeeting.instructors.trim() === "—") currMeeting.instructors = [];
		else {
			currMeeting.instructors = currMeeting.instructors
				.trim()
				.split("\n")
				.map((item) => item.trim());
		}
		currMeeting.space = meeting.querySelector(".colAvail").innerText.trim();
		currMeeting.waitlist = meeting.querySelector(".colWait").innerText.trim();
		currMeeting.notes = meeting.querySelector(".colNotes").innerText.trim();
		currMeeting.times = days;
		currMeeting.activityType = activity.substring(0, 3);
		currMeeting.activityCode = activity.substring(3);
		if (!(currMeeting.activityType in meetings)) {
			meetings[currMeeting.activityType] = [];
		}
		meetings[currMeeting.activityType].push(currMeeting);
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
