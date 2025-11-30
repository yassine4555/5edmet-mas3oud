import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from models import db, File, User
from utils.security import require_api_key
from werkzeug.utils import secure_filename
import uuid

files_bp = Blueprint('files', __name__)

@files_bp.route('/upload', methods=['POST'])
@require_api_key
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    user_email = request.form.get('user_email')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not user_email:
        return jsonify({"error": "user_email is required"}), 400

    # Verify user exists
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        filename = secure_filename(file.filename)
        file_id = f"file_{uuid.uuid4().hex}"
        
        # Ensure upload directory exists
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        # Save file
        # To avoid filename collisions, we might want to prepend file_id or use it as filename
        # For this implementation, we'll use the original filename but be careful
        save_path = os.path.join(upload_folder, filename)
        file.save(save_path)
        
        new_file = File(
            file_id=file_id,
            filename=filename,
            original_filename=file.filename,
            size=os.path.getsize(save_path),
            content_type=file.content_type,
            uploaded_by=user_email,
            file_path=save_path
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "filename": filename,
            "file_id": file_id,
            "url": f"/file/get/{filename}"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@files_bp.route('/get/<filename>', methods=['GET'])
@require_api_key
def get_file(filename):
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@files_bp.route('/getAll', methods=['GET'])
@require_api_key
def get_all_files():
    user_email = request.args.get('user_email')
    
    query = File.query
    if user_email:
        query = query.filter_by(uploaded_by=user_email)
        
    files = query.all()
    return jsonify({"files": [f.to_dict() for f in files]}), 200
