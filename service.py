def match(method):
    if method == 'qlearning':
        return 'QlearningFirm'
    if method == 'intuitive':
        return 'DianaFirm'
    if method == 'extrapolation':
        return 'IntuitiveFirm'
    return "RandomFirm"