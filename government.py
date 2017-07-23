class Government:

    def __init__(self, model_config, run_config):
        for parameter in model_config:
            if parameter:
                setattr(self, parameter, run_config[parameter])
