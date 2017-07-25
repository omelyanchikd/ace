class OutsideWorld:

    def __init__(self, run_config):
        for parameter in run_config:
            setattr(self, parameter, run_config[parameter])
