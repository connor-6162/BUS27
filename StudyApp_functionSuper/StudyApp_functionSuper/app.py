from flask import Flask
from config import Config
from extensions import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

import routes
app.register_blueprint(routes.bp)

print("ROUTES FILE:", routes.__file__)
print("URL MAP:", app.url_map)

if __name__ == "__main__":
    app.run(debug=True)