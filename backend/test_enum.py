import json
import enum

class Role(str, enum.Enum):
    ADMIN = 'ADMIN'

print(json.dumps({'role': Role.ADMIN}))
