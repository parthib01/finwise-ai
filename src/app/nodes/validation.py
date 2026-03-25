def validate_permission(state):
    # Replace with real logic
    if not state.user_id:
        raise Exception("Unauthorized")

    return state