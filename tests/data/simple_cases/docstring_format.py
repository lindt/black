class MyClass:
    def method(self):
        """
        ordinary documentation

        but now some code:
        >>>  print( "test" )
        "test"
        >>>  print(
        ...     1
        ... )
        >>> print(1,2,3,)
        """
        pass


# output

class MyClass:
    def method(self):
        """
        ordinary documentation

        but now some code:
        >>> print("test")
        "test"
        >>> print(1)
        >>> print(
        ...     1,
        ...     2,
        ...     3,
        ... )
        """
        pass
