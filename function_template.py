# -*- coding: utf-8 -*-
"""
This file is simply to show the thing we require/desire in our functions so they are consistent
"""

def test_function(x:       list,
                  name:    str,
                  year:    int = 2024,
                  comment: str|None = None
                  ) -> tuple[str, list]:
    '''
    This is a test function to show what structure is useful when defining a function.
    It includes typehints in the input parameters, a description of the function, and type hints for the output parameters in the tuple.

    Parameters
    ----------
    x : list
        DESCRIPTION. An input list
    name : str
        DESCRIPTION. My name
    year : int, optional
        DESCRIPTION. The default is 2024. Current year
    comment : str|None, optional
        DESCRIPTION. The default is None. Comment about life.

    Returns
    -------
    tuple[str, list]
        DESCRIPTION. Output parameters, the first is a string describing whether a comment was provided, the second is the unchanged input list.

    '''
    if comment:
        comment_present = 'yes'
    else:
        comment_present = 'no'
        
    return x,comment_present

