def create_chaining(prompt, model, parser):
    result = prompt | model | parser

    return result