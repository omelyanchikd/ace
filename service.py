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
    if method == 'hierarchical':
        return 'RuleFirm'
    if method == 'classification_decision_tree':
        return 'TreeFirm'
    if method == 'perceptron':
        return 'AnnFirm'
    return "RandomFirm"