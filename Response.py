from random import choice, randint

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Please enter a message.'
    elif "hello" in lowered:
        return "Hello!"
    elif "rolldice" in lowered:
        return str(randint(1, 6))
    else:
        return choice([
            "I'm sorry, I don't understand.",
            "I don't know what you mean by that.",
            "I'm not sure what you're asking.",
            "I don't know what you're talking about."
        ])




