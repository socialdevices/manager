def precondition(f):
    f.SDMethodType = 'pre'
    return f

def body(f):
    f.SDMethodType = 'body'
    return f

def deviceInterface(c):
    return c

