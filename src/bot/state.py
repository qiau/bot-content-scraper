import time

user_states = {}

def set_state(user_id, state):
    user_states[user_id] = {
        "state": state,
        "time": time.time()
    }

def get_state(user_id):
    data = user_states.get(user_id)

    if not data:
        return None

    if time.time() - data["time"] > 600:
        user_states.pop(user_id, None)
        return None

    return data["state"]

def clear_state(user_id):
    user_states.pop(user_id, None)