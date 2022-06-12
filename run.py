import os
import threading
if os.name == "nt":
    t1 = threading.Thread(target=os.system, args=(r"python bot\main.py",))
    t2 = threading.Thread(target=os.system, args=(r"python bot\events.py",))
    t1.start()
    t2.start()
else:
    os.system("python3 bot/main.py & python3 bot/events.py")