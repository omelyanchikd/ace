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
    if method == 'random':
        return "RandomFirm"
    if method == 'oligopoly':
        return "OligopolyFirm"
    return "ERROR"


def toStr(n, base):
   convertString = "0123456789ABCDEF"
   if n < base:
      return convertString[n]
   else:
      return toStr(n//base,base) + convertString[n % base]


def get_action_list(action):
    action_list = []
    action_dict = {'0': 0, '1': 1, '2': -1}
    for c in action:
        action_list.append(action_dict[c])
    return action_list