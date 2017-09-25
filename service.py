def match(method):
    if method == 'qlearning':
        return 'QlearningFirm'
    if method == 'intuitive':
        return 'DianaFirm'
    if method == 'extrapolation':
        return 'IntuitiveFirm'
    if method == 'moses':
        return 'MosesFirm'
    if method == 'nonconscious':
        return 'NonconsciousFirm'
    if method == 'rational':
        return 'RationalFirm'
    return "RandomFirm"