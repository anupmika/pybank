class SingletonMeta(type):
    """
    Metaclass that ensures only one instance of a class is created.

    The Singleton pattern can be implemented in several ways in Python,
    including using a base class, decorator, or metaclass. This implementation
    uses a metaclass because it allows the Singleton behavior to be applied
    without modifying the class itself.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Create and return a single instance of the class.

        Any subsequent calls to create an instance of the same class will
        return the previously created instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]
