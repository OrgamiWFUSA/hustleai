def generate_checklist(idea):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""Take this full side hustle idea and break it into 7–15 specific, actionable steps to launch it.
Include realistic due dates starting from today, spread over 30 days.
Format each step as: 'Step description - YYYY-MM-DD'

Idea:
{idea}"""
            }]
        )
        lines = response.choices[0].message.content.strip().split('\n')
        steps = []
        base = datetime.now()
        for i, line in enumerate(lines):
            if ' - ' in line:
                goal, date_str = line.split(' - ', 1)
                try:
                    due = datetime.strptime(date_str.strip(), "%Y-%m-%d")
                except:
                    due = base + timedelta(days=i + 1)
                steps.append({"goal": goal.strip(), "due": due.strftime("%Y-%m-%d")})
        return steps[:15]  # Max 15 steps
    except Exception as e:
        st.error("AI failed to generate checklist")
        return []