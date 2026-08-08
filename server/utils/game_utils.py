import math

def calculate_multiplier(total_room_coins: int, correct_candidate_coins: int) -> float:
    """Calculates the dynamic multiplier per round."""
    if correct_candidate_coins == 0:
        return 0.0
    return round(math.sqrt(math.sqrt(total_room_coins / correct_candidate_coins)), 3)

def calculate_speed_bonus(lock_in_time: float) -> float:
    """Returns continuous scale speed bonus based on lock-in time."""
    if lock_in_time <= 5.0:
        return 1.05
    elif lock_in_time <= 10.0:
        return 1.04
    elif lock_in_time <= 15.0:
        return 1.03
    elif lock_in_time <= 20.0:
        return 1.02
    elif lock_in_time <= 25.0:
        return 1.01
    return 1.00

def calculate_risk_bonus(max_allocation_amount: int) -> float:
    """Calculates Risk Bonus based on Round 1 single-candidate stake percentage."""
    percentage = (max_allocation_amount / 10000.0) * 100
    if percentage == 100:
        return 1.10
    elif 75 <= percentage <= 99:
        return 1.07
    elif 50 <= percentage <= 74:
        return 1.04
    elif 1 <= percentage <= 49:
        return 1.02
    return 1.00

def get_round_weight(round_number: int) -> float:
    """Weighted contributions per round."""
    weights = {1: 1.0, 2: 1.5, 3: 2.0}
    return weights.get(round_number, 1.0)