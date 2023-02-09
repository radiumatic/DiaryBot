import os
import threading
if os.name == "nt":
    t1 = threading.Thread(target=os.system, args=(r"python bot\main.py",))
    t1.start()
else:
    os.system("python3 bot/main.py")
