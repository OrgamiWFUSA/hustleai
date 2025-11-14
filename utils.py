def generate_checklist(idea):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        prompt = f"""
You are a world-class startup coach. Take this full side hustle idea and turn it into a 30-day launch roadmap.

Generate 7–15 headline goals (major milestones). For each headline goal:
- List 3–7 daily or weekly sub-tasks (what to do each day/week)
- Assign a realistic due date (YYYY-MM-DD), starting today, spread over 30 days

Format exactly like this:
**Goal 1: [Headline] - YYYY-MM-DD**
- [Daily/Weekly Task 1]
- [Daily/Weekly Task 2]
...

Idea:
{idea}
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.choices[0].message.content.strip()
        lines = text.split('\n')
        
        goals = []
        current = None
        for line in lines:
            line = line.strip()
            if line.startswith('**') and ' - ' in line:
                if current:
                    goals.append(current)
                parts = line.split(' - ', 1)
                goal_title = parts[0][2:].strip()  # Remove **
                due_date = parts[1].strip() if len(parts) > 1 else ""
                current = {"goal": goal_title, "due": due_date, "sub_tasks": []}
            elif line.startswith('- ') and current:
                current["sub_tasks"].append(line[2:].strip())
        
        if current:
            goals.append(current)
        
        # Validate/fix dates
        base = datetime.now()
        for i, g in enumerate(goals):
            try:
                due = datetime.strptime(g["due"], "%Y-%m-%d")
            except:
                due = base + timedelta(days=i*2 + 3)  # Spread out
            g["due"] = due.strftime("%Y-%m-%d")
        
        return goals[:15]  # Max 15 goals
    except Exception as e:
        st.error("AI failed to generate checklist")
        return []