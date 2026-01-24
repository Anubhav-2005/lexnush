from flask_frozen import Freezer
from app import app

# This configures the freezer to generate URLs relative to the root
# ensuring your CSS and JS links work perfectly on Netlify.
app.config['FREEZER_RELATIVE_URLS'] = True

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()