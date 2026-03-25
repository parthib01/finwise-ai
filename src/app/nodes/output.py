def validate_output(state):
    if not state.response:
        raise Exception("Empty response")

    # Add more checks later
    return state