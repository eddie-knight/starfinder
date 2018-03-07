class StarfinderException(Exception):
    def __init__(self, **keys):
        super().__init__(self.message % keys)

    @property
    def message(self):
        raise NotImplementedError('Message not set!')

class ConfigKeyNotFound(LifeloopException):
    message = ("The requested key '%(key)s' does not exist in the "
               "application configuration")