# Test type annotations
from typing import List

def bar(x : int) -> List[int]:
    # AnnAssign: Annotated Assignment
    ibar : int = x
    return [ibar, x]

def foo(x : int) -> List[int]:
    # next line basically an empty annotation, since there is no assignment in the AnnAssign
    ifoo: int
    ifoo = x
    return [x, ifoo]

print(bar(5))
print(foo(4))

