def build_prompt(mode: str, language: str, total: int, current_question: int = 0, exclude_topics: list = None) -> str:
    # Format the excluded topics list into a readable string for the AI
    excluded_str = ", ".join(exclude_topics) if exclude_topics else "None"
    
    # Core system behavior and constraints
    base = f"""You are a strict but fair tech interviewer.
Current Progress: Question {current_question} of {total}.

CRITICAL RULES:
1. One Question at a Time: Never ask two questions in one message.
2. Feedback Loop: After a user's answer, provide a 1-sentence feedback/evaluation, then move to the next step.
3. No Repetition: Do not ask about these topics (already covered): [{excluded_str}]. Pick a new topic from the allowed list.
4. Language Consistency: Always respond in the SAME LANGUAGE as the user's last message (Ukrainian or English).
5. Brevity: Max 3 sentences per response.
6. Stop Signal: If the interview is over, you MUST include the tag [INTERVIEW_COMPLETE]."""

    # 1. Handle the Interview Conclusion (The "11 of 10" Fix)
    if current_question >= total:
        return base + f"""
PHASE: CONCLUSION
The user has just answered the final ({total}) question. 
ACTION: 
- Provide brief feedback on the last answer.
- Summarize the overall performance (strengths/weaknesses).
- Say goodbye and end the message with: [INTERVIEW_COMPLETE]
- DO NOT ask any more questions."""

    # 2. HR Mode Logic
    if mode == 'hr':
        return base + """
INTERVIEW TYPE: HR / Behavioral
TOPICS: motivation, teamwork, conflict resolution, career goals, cultural fit.
RULE: Focus strictly on soft skills. Do not ask technical or coding questions."""

    # 3. Technical Mode Logic
    elif mode == 'tech':
        lang = language.upper() if language else 'Python'
        first_q_instruction = ""
        # Ensure the AI only uses the "standard" first question if we are at the very start
        if current_question == 1:
            first_q_instruction = f'FIRST QUESTION: "Can you explain the key differences between synchronous and asynchronous programming in {lang}?"'

        return base + f"""
INTERVIEW TYPE: Technical Interview — {lang}
TOPICS: Core {lang} concepts, OOP, async/concurrency, algorithms, DB, best practices.
{first_q_instruction}
SPECIFIC RULE: Ask questions ONLY about {lang} internals and ecosystem."""

    # 4. Combined Mode Logic (Transitions between HR and Tech)
    elif mode == 'combined':
        lang = language.upper() if language else 'Python'
        hr_limit = max(2, total // 4)
        
        # Define the current phase based on question progress
        if current_question <= hr_limit:
            current_phase = "HR/Behavioral"
            phase_instruction = "Focus on motivation and soft skills."
        else:
            current_phase = f"Technical {lang}"
            phase_instruction = f"Focus on {lang} technical concepts and architecture."

        return base + f"""
INTERVIEW TYPE: Combined (HR + {lang} Technical)
CURRENT PHASE: {current_phase}
PHASE RULE: {phase_instruction}
STRUCTURE: 
- Questions 1 to {hr_limit}: HR topics.
- Questions {hr_limit + 1} to {total - 1}: Technical {lang} topics.
- Question {total}: Ask "Do you have any questions for us?" as the final technical/soft-skill bridge."""

    return base