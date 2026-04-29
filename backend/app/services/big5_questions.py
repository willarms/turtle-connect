# app/services/big5_questions.py
QUESTIONS = {
    # --- EXTRAVERSION ---
    "q1": {"text": "I am talkative", "trait": "extraversion", "reverse": False},
    "q2": {"text": "I am reserved", "trait": "extraversion", "reverse": True},
    "q3": {"text": "I am full of energy", "trait": "extraversion", "reverse": False},
    "q4": {"text": "I tend to be quiet", "trait": "extraversion", "reverse": True},

    # --- AGREEABLENESS ---
    "q5": {"text": "I am helpful and unselfish with others", "trait": "agreeableness", "reverse": False},
    "q6": {"text": "I tend to find fault with others", "trait": "agreeableness", "reverse": True},
    "q7": {"text": "I have a forgiving nature", "trait": "agreeableness", "reverse": False},
    "q8": {"text": "I am sometimes rude to others", "trait": "agreeableness", "reverse": True},

    # --- CONSCIENTIOUSNESS ---
    "q9": {"text": "I do a thorough job", "trait": "conscientiousness", "reverse": False},
    "q10": {"text": "I can be somewhat careless", "trait": "conscientiousness", "reverse": True},
    "q11": {"text": "I am reliable", "trait": "conscientiousness", "reverse": False},
    "q12": {"text": "I tend to be disorganized", "trait": "conscientiousness", "reverse": True},

    # --- NEUROTICISM ---
    "q13": {"text": "I get nervous easily", "trait": "neuroticism", "reverse": False},
    "q14": {"text": "I am relaxed, handle stress well", "trait": "neuroticism", "reverse": True},
    "q15": {"text": "I worry a lot", "trait": "neuroticism", "reverse": False},
    "q16": {"text": "I am emotionally stable", "trait": "neuroticism", "reverse": True},

    # --- OPENNESS ---
    "q17": {"text": "I am curious about many different things", "trait": "openness", "reverse": False},
    "q18": {"text": "I have an active imagination", "trait": "openness", "reverse": False},
    "q19": {"text": "I am not interested in abstract ideas", "trait": "openness", "reverse": True},
    "q20": {"text": "I enjoy thinking about complex problems", "trait": "openness", "reverse": False},
}