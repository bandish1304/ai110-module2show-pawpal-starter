# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
	- My initial UML design separated data objects from planning logic. I focused on modeling the owner, pet, and tasks as core entities, and then using a scheduler class to generate a realistic daily care plan from those inputs.

- What classes did you include, and what responsibilities did you assign to each?
	- I included four classes: Owner, Pet, Task, and Scheduler. Owner stores time limits and preferences (like available minutes per day and preferred schedule). Pet stores pet-specific information and maintains the list of care tasks. Task represents each care activity with attributes like title, duration, priority, and whether it is required. Scheduler takes the owner constraints and pet tasks, ranks and filters tasks, and builds the daily plan in a feasible order.

**b. Design changes**

- Did your design change during implementation?
	- Yes. After reviewing my class skeleton, I made a few design-level changes to improve object relationships and avoid future logic issues.
- If yes, describe at least one change and why you made it.
	- First, I added a task_id attribute to Task and changed Pet.remove_task() to remove by ID instead of title. I made this change because task titles can repeat (for example, multiple "Walk" tasks), and using IDs creates a more reliable relationship between Pet and Task objects.
	- Second, I added a get_task_by_id() method to Pet so the scheduler or UI can retrieve a specific task directly instead of scanning by title.
	- Third, I added refresh_inputs() and a  dictionary. This makes the data flow clearer (reload tasks and constraints in one place) and prepares the scheduler to explain why each task was selected or skipped, which supports the project requirement to justify the daily plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
