import spacy

# Load the language model
nlp = spacy.load('en_core_web_sm')

def question_to_statement(question, prediction_info):
    # Parse the question
    doc = nlp(question)
    
    # Initialize variables
    modal = None
    subject = None
    main_verb = None
    rest_of_sentence = []
    
    # Iterate over tokens to find the modal, subject, and main verb
    for token in doc:
        if token.tag_ == 'MD':
            modal = token
        elif token.dep_ == 'nsubj' and not subject:
            subject = token
            # Get the entire noun phrase for the subject
            while subject.n_lefts > 0:
                subject = list(subject.lefts)[0]
        elif subject and token.head == subject.head and token.dep_ != 'aux':
            main_verb = token
        elif main_verb and token.idx > main_verb.idx and token.text != '?':
            rest_of_sentence.append(token.text_with_ws)

    # Check if we have successfully identified the parts
    if not modal or not subject or not main_verb:
        missing_parts = ', '.join([
            part for part, present in [('modal', bool(modal)), 
                                       ('subject', bool(subject)), 
                                       ('main_verb', bool(main_verb))] if not present
        ])
        return f"Missing elements: {missing_parts}. The question format is not recognized for conversion."

    # Reconstruct the statement
    statement = (
        f"There is a {prediction_info} chance that {subject.text.capitalize()} "
        f"{modal.text.lower()} {main_verb.text} {''.join(rest_of_sentence).strip()} "
        f"according to Metaculus prediction community."
    ).replace('  ', ' ')

    return statement.strip()

# Example usage
question = "Will one of the first AGI claim to be conscious?"
prediction_info = "45%"
statement = question_to_statement(question, prediction_info)
print(statement)
