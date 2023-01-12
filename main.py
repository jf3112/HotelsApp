import os
from website import create_app
import psycopg2

app = create_app()
app.config['SECRET KEY'] = os.urandom(10)


if __name__ == '__main__':
    app.run(debug=True)


