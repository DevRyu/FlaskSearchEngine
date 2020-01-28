import os
import sys
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(parent_dir)

from apis import app

if __name__ == '__main__':
    app.run(host="127.0.0.1", port="5000",debug = True)
