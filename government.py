class Government:

    def __init__(self, model_config, run_config):
        for parameter in run_config:
            if parameter not in model_config or model_config[parameter]:
                setattr(self, parameter, run_config[parameter])
