from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'})
        
        # Ensure the file is in the audios directory
        audio_dir = Path('audios')
        file_path = audio_dir / filename
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': 'File not found'})
        
        # Delete the file
        file_path.unlink()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/audios/<path:filename>')
def serve_audio(filename):
    return send_from_directory('audios', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 