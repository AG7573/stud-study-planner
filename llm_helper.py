import requests

def get_schedule_summary(sessions, subjects):
    try:
        schedule_text = ""
        for s in sessions:
            schedule_text += f"- {s.task.title} on {s.date}: {s.hours} hours\n"

        subjects_text = ", ".join(f"{sub.title} (exam {sub.exam_date})" for sub in subjects)

        prompt = (
            f"Here is a student's study schedule:\n{schedule_text}\n"
            f"Subjects and exam dates: {subjects_text}\n\n"
            "Write a short, encouraging 2-3 sentence summary of this schedule "
            "for the student. Mention the busiest day if there is one."
        )

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()

        return response.json()["response"]

    except Exception as e:
        print(f"LLM summary failed: {e}")
        return None