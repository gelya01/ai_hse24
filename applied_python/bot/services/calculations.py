def calculate_daily_calories(weight, height, age, gender, activity, goal):
    if gender.lower() == "мужчина":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * activity

    if goal.lower() == "похудение":
        return tdee * 0.85
    elif goal.lower() == "набор массы":
        return tdee * 1.15
    return tdee


def calculate_daily_water(weight, activity):
    base_water = weight * 0.03
    return base_water + (activity - 1.2) * 0.4  # на несидячую активность больше воды
