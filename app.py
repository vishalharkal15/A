import os

# Suppress TensorFlow warnings about GPU/CUDA
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=INFO, 2=WARNING, 3=ERROR
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable GPU usage

from flask import Flask, send_from_directory
from flask_cors import CORS
from mtcnn import MTCNN
from keras_facenet import FaceNet

# Initialize Flask
app = Flask(__name__, static_folder='dist', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

# Initialize DB
from models import init_db
db, Attendance, Student = init_db(app)

# Initialize FaceNet & MTCNN
detector = MTCNN()
embedder = FaceNet()

# Register routes
from routes import register_routes
register_routes(app, db, Attendance, detector, embedder)

# Serve React frontend - must be after API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Don't serve static files for API routes or enroll/recognize/update-face endpoints
    if path.startswith('api/') or path in ['enroll', 'recognize', 'update-face']:
        return {'error': 'Not found'}, 404
    
    # Serve static files if they exist
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    # Otherwise serve index.html for client-side routing
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0", 
        port=port
    )
