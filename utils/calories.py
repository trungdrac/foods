DEFAULT_HEIGHT = 150
DEFAULT_WEIGHT = 50
DEFAULT_FACTOR = 1
DEFAULT_AGE = 20
DEFAULT_GENDER = True

def bmr(weight=DEFAULT_WEIGHT, height=DEFAULT_HEIGHT, gender=DEFAULT_GENDER, age=DEFAULT_AGE, factor=DEFAULT_FACTOR):
    '''
        Basal Metabolic Rate
        Please visit https://en.wikipedia.org/wiki/Basal_metabolic_rate
    '''
    w = 13.7516 if gender else 9.5634
    h = 5.0003 if gender else 1.8496
    a = 6.7550 if gender else 4.6756
    add = 66.4730 if gender else 655.0955

    total = w * weight + h * height - a * age + add
    factored_total = total*factor

    return round(factored_total)