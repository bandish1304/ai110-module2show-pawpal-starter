from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_data() -> Owner:
	owner = Owner(
		name="Ben",
		available_minutes_per_day=45,
		preferred_schedule="morning",
		task_preferences=["exercise", "feeding", "daily"],
		max_tasks_per_day=4,
	)

	dog = Pet(name="Jack", species="dog", breed="Corgi", age=4, energy_level="high")
	cat = Pet(name="Leah", species="cat", breed="Siamese", age=3, energy_level="medium")

	dog.add_task(
		Task(
			task_id="jack-breakfast",
			title="Breakfast",
			description="Serve breakfast and refill water.",
			duration_minutes=10,
			priority="high",
			category="feeding",
			preferred_time="morning",
			is_required=True,
		)
	)
	dog.add_task(
		Task(
			task_id="jack-walk",
			title="Morning Walk",
			description="Neighborhood walk before work.",
			duration_minutes=20,
			priority="high",
			category="exercise",
			preferred_time="morning",
			is_required=True,
		)
	)

	cat.add_task(
		Task(
			task_id="leah-medication",
			title="Medication",
			description="Give daily medication with a treat.",
			duration_minutes=5,
			priority="high",
			category="medical",
			preferred_time="morning",
			is_required=True,
		)
	)
	cat.add_task(
		Task(
			task_id="leah-play",
			title="Laser Play",
			description="Interactive play session in the living room.",
			duration_minutes=15,
			priority="medium",
			category="exercise",
			preferred_time="evening",
		)
	)

	owner.add_pet(dog)
	owner.add_pet(cat)
	return owner


def print_schedule(owner: Owner) -> None:
	scheduler = Scheduler(owner)
	todays_schedule = scheduler.generate_schedule()

	print("Today's Schedule")
	print("=" * 40)
	print(owner.get_summary())
	print()

	for index, task in enumerate(todays_schedule, start=1):
		pet_name = scheduler.task_pet_lookup.get(task.task_id, "Unknown pet")
		reason = scheduler.selection_reasons.get(task.task_id, "Selected by the scheduler.")
		print(f"{index}. {pet_name} - {task.title}")
		print(f"   Time: {task.duration_minutes} minutes")
		print(f"   Priority: {task.priority}")
		print(f"   Preferred time: {task.preferred_time}")
		print(f"   Reason: {reason}")
		print()

	if scheduler.unscheduled_tasks:
		print("Tasks not scheduled today:")
		for task in scheduler.unscheduled_tasks:
			pet_name = scheduler.task_pet_lookup.get(task.task_id, "Unknown pet")
			reason = scheduler.selection_reasons.get(task.task_id, "Not scheduled.")
			print(f"- {pet_name}: {task.title} ({task.duration_minutes} minutes) -> {reason}")


if __name__ == "__main__":
	demo_owner = build_demo_data()
	print_schedule(demo_owner)
