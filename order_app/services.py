def validate_card(text):
    if int(text) % 2 != 0:
        return False
    elif int(text[-1]) == 0:
        return False
    else:
        return True
