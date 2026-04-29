from app.services.big5_questions import QUESTIONS

def score_big5(answers: dict):
    scores = {
        "openness": 0,
        "conscientiousness": 0,
        "extraversion": 0,
        "agreeableness": 0,
        "neuroticism": 0
    }

    counts = {k: 0 for k in scores}

    for q_id, answer in answers.items():
        if q_id not in QUESTIONS:
            continue

        q = QUESTIONS[q_id]
        trait = q["trait"]

        # reverse scoring (1–5 scale)
        if q["reverse"]:
            answer = 6 - answer

        scores[trait] += answer
        counts[trait] += 1

    # normalize (average per trait)
    for trait in scores:
        if counts[trait] > 0:
            scores[trait] = round(scores[trait] / counts[trait], 2)

    return scores


def summarize_personality(scores):
    top_trait = max(scores, key=scores.get)

    descriptions = {
        "extraversion": "Outgoing and energetic",
        "agreeableness": "Compassionate and cooperative",
        "conscientiousness": "Organized and dependable",
        "neuroticism": "Emotionally sensitive",
        "openness": "Creative and curious"
    }

    return {
        "dominant_trait": top_trait,
        "description": descriptions[top_trait]
    }

def interpret_big5(scores):
    interpretation = {}

    for trait, score in scores.items():
        if score >= 4:
            level = "High"
        elif score >= 3:
            level = "Moderate"
        else:
            level = "Low"

        interpretation[trait] = {
            "score": score,
            "level": level
        }

    return interpretation