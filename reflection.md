# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design was very simple. It had four classes, Owner, Pet, Task, and Scheduler, that held basic information and could perform a few simple actions. The three main actions I designed around were entering a task, editing a task, and generating a plan. For relationships, an Owner owns one or more Pets, a Pet has tasks it needs done, and the Scheduler uses the Owner's information to plan for the Pet and manage its tasks. At first the Scheduler only worked with one pet at a time and kept its own list of tasks.


- What classes did you include, and what responsibilities did you assign to each?
In my initial UML design, I had the classes Pet, Owner, Scheduler, and Task. Within the Pet and Owner classes, I made sure that the classes could hold important information about each class, such as the owner's available time and preferences and the pet's species and breed. Scheduler and Task classes are related to handling how the day gets planned. Task represents a single activity, like a walk or feeding, with a duration and a priority. Scheduler is the "brain" of the app that lets the user enter and edit tasks and then generates a plan based on how much time the owner has and how important each task is.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

could handle an Owner with more than one pet instead of only one pet at a time. I also made task priorities sortable so that the Scheduler could better organize tasks based on what is most important to the owner. I made these changes because they made the system more flexible and realistic for a pet-care scheduling application.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Constraints the scheduler considers are time and priority. The scheduler considers both time and priority. The owner can assign each task a priority of high, medium, or low and can also specify when a task should be completed. The Scheduler first organizes tasks based on their scheduled time and then uses priority to help determine which tasks should be completed when there are time constraints.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler prioritizes high-priority tasks when the owner's available time is limited. This means some lower-priority tasks may be skipped even if there would be enough time for several smaller tasks. This tradeoff is reasonable because the goal is to make sure the owner's most important pet-care responsibilities are completed before less important tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI tools to help me thinking outside the box with brainstorming for additional features to add to my project. AI tools helped with thinking of extra edge cases and explaining some functions that I did not understand before. For example, I asked to explain how st.session_state worked. 

Questions that were most helpful were :

 "Explain st.session_state. How do I check if an object  already exists in the "vault" of the session before creating a new one?"

 "Are there any missing relationships or potential bottlenecks within @pawpal_system.py?"




**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
A moment where I did not accept an AI suggestin as-is was during the beginning when I asked the agent to generate the first version of the pawpal_system.py file. The first version had an almost fully implemented file, and I rejected it to only have a skeleton of the file with no implementation or defaults made for me. I wanted to keep control of the design. 

I evaluated AI suggestions by running pytest and python main.py in the terminal myself and comparing the results to the expected behavior.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the main behaviors that the scheduler depends on:

- **Basic task actions:** marking a task complete changes its status, and adding a task to a pet increases that pet's task count.
- **Sorting:** tasks come out in time order even when they are added out of order, a time like "8:00" sorts before "10:00", early and late times like midnight sort correctly, and "anytime" tasks go last. When two tasks have the same priority, the shorter one goes first.
- **Filtering:** tasks can be separated into completed and pending, across all of the owner's pets.
- **Recurring tasks:** completing a daily task creates a new one for tomorrow, a weekly task creates one for next week, and a one-time task does not repeat. The new task keeps the same details, gets added to the right pet, and only shows up in tomorrow's plan, not today's.
- **Conflict detection:** two tasks at the same time give a warning, whether they are for the same pet or different pets. Three tasks at one time only give one warning, "anytime" tasks never conflict, and tasks that were skipped or are on different days do not count.

These tests were important because the scheduler makes a lot of small decisions on its own, and a bug in any of them would give the owner a wrong plan without any error. For example, before I added the sorting test, "8:00" was sorting after "10:00" because the times were being compared as text. Writing tests for edge cases like that made sure the plan the owner sees is actually in the right order.


**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

All 22 tests pass, and they cover the main scheduling paths: sorting, recurring tasks, conflict detection and the time budget. I have a confidence level of 4/5. It's not a 5 because of a few known gaps:

- Conflict detection only catches identical start times, not overlapping durations.
- Completing the same recurring task twice creates a duplicate next occurrence.
- A failed `edit()` leaves the invalid value on the task.

If I had more time, I would write tests for those gaps first, like two tasks that overlap but start at different times (an 08:00 walk for 30 minutes and an 08:15 task). I would also test what happens when the owner has 0 minutes available, and when a single task is longer than the owner's whole day.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am happy that the extra features, like the sorting tasks and handling multiple pets, work so well. It was difficult to make the sorting tasks not overcomplicated. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would want to redesign the UI to make it a bit more aesthetically pleasing and fun for the user to interact with. I would also make the generated plan more personalized based on the owner's routines and each pet's needs. Another feature I would add is reminder notifications so that owners are alerted when it is time to complete an important task.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

An important thing I learned about system design is that it will not look perfect on the first try, and it will take working on the actual project to finalize the design.  However, having an initial design does help with the overall idea and structure of your program. 