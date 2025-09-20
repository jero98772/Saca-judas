def iterative_sqrt(n,x,A):
    """Iterative SQRT algorithm implementation."""
    step_by_step=""
    def formula(x,A):
        return sqrt(((x**3)+A)/(2*x))
    
    step_by_step+=""
    for i in range(n):
        x=formula(x,A)
    return x, step_by_step ,(0,0)