from datetime import datetime
from datetime import date
from datetime import timedelta

PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}

def calculate_urgency(priority, due_date):
    days_until_due = (due_date - datetime.now().date()).days
    clamped_days = max(days_until_due, 1)
    weight = PRIORITY_WEIGHTS[priority]
    urgency_score = weight / clamped_days
    return urgency_score

LIST_OF_TASKS = [ 
                    {"id": 1, "title": "physics", "priority": "high", "due_date": datetime.now().date() + timedelta(days=2), "estimated_hours": 5},
                    {"id": 2, "title": "maths", "priority": "medium", "due_date": datetime.now().date() + timedelta(days=5), "estimated_hours": 2},
                    {"id": 3, "title": "History", "priority": "low", "due_date": datetime.now().date() + timedelta(days=10), "estimated_hours": 3},
                    {"id": 4, "title": "PDS", "priority": "high", "due_date": datetime.now().date() + timedelta(days=1), "estimated_hours": 25}
                ]   
def sort_by_urgency(tasks):
    sorting = sorted(tasks, key=lambda task:
                     calculate_urgency(task["priority"], task["due_date"]), reverse=True)
    for task in tasks:
        task["remaining_hours"] = task["estimated_hours"]
    return sorting

def day_by_day_allocation(tasks):
    schedule = []
    overcommitted = []
    for task in tasks:
        current_date = datetime.now().date()
        available_days = (task["due_date"] - current_date).days
        total_time = available_days * 6
        clamped_days = max((task["due_date"] - current_date).days, 1) * 6
        if task["estimated_hours"] > total_time:
            task["remaining_hours"] = 0
            overcommitted_record = {"todays_date": current_date, "task_title": task["title"]}
            overcommitted.append(overcommitted_record)
    while any(task["remaining_hours"] > 0 for task in tasks):
        hours_left_today = 6
        while hours_left_today > 0 and any(task["remaining_hours"] > 0 for task in tasks):
            for task in tasks:
                if task["remaining_hours"] > 0 and current_date > task["due_date"]:
                    task["remaining_hours"] = 0
                    overcommitted_record = {"todays_date": current_date, "task_title": task["title"]}
                    overcommitted.append(overcommitted_record)
                    continue
                if task["remaining_hours"] > 0:
                    amount_of_time = min(hours_left_today, task["remaining_hours"])
                    task["remaining_hours"] -= amount_of_time
                    hours_left_today -= amount_of_time
                    schedule_record = {"todays_date": current_date, "task_title": task["title"], "allocated_amount": amount_of_time, "task_id": task["id"]}
                    schedule.append(schedule_record)
                    break
        current_date += timedelta(days=1)
    return schedule, overcommitted

print(sort_by_urgency(LIST_OF_TASKS))

result = day_by_day_allocation(sort_by_urgency(LIST_OF_TASKS))
for entry in result:
    print(entry)       

if __name__ == "__main__":
    print(calculate_urgency("high", datetime.now().date() + timedelta(days=2)))
    print(calculate_urgency("medium", datetime.now().date() + timedelta(days=5)))
    print(calculate_urgency("low", datetime.now().date() + timedelta(days=10)))
    print(calculate_urgency("high", datetime.now().date() + timedelta(days=1)))