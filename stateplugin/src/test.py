import os
pathname = os.path.abspath(__file__)
print pathname.replace( os.path.basename(pathname), '')

