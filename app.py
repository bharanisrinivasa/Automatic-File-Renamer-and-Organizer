import os
import shutil
import math
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import webview

# ==========================================
# 1. FILE MANAGEMENT BACKEND LOGIC
# ==========================================

def get_file_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_directory_contents(directory_path):
    contents = []
    try:
        entries = os.scandir(directory_path)
    except Exception as e:
        return [], str(e)

    for entry in entries:
        try:
            stat = entry.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            is_dir = entry.is_dir()
            
            if is_dir:
                size_str = ""
                type_str = "File folder"
            else:
                size_str = get_file_size(stat.st_size)
                _, ext = os.path.splitext(entry.name)
                type_str = f"{ext[1:].upper()} File" if ext else "File"
            
            contents.append({
                "name": entry.name,
                "path": entry.path,
                "is_dir": is_dir,
                "size": size_str,
                "modified": mod_time,
                "type": type_str
            })
        except OSError:
            continue
            
    contents.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    return contents, None

def get_local_drives():
    import string
    drives = []
    bitmask = os.popen("fsutil fsinfo drives").read()
    if bitmask:
        import re
        drives = re.findall(r'[A-Z]:\\', bitmask)
    else:
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                drives.append(drive_path)
    return drives

def open_file(path):
    try:
        if os.name == 'nt':
            os.startfile(path)
        else:
            import subprocess
            subprocess.Popen(['open', path] if os.sys.platform == 'darwin' else ['xdg-open', path])
        return True, None
    except Exception as e:
        return False, str(e)

def rename_item(old_path, new_name):
    directory = os.path.dirname(old_path)
    new_path = os.path.join(directory, new_name)
    try:
        os.rename(old_path, new_path)
        return True, None
    except Exception as e:
        return False, str(e)

def organize_files_by_extension(directory_path):
    try:
        files = []
        for filename in os.listdir(directory_path):
            full_path = os.path.join(directory_path, filename)
            if os.path.isfile(full_path):
                if filename.startswith('.'):
                    continue
                ext = os.path.splitext(filename)[1][1:]
                if ext:
                    files.append((filename, ext, full_path))
                    
        organized_count = 0
        for filename, ext, full_path in files:
            folder = os.path.join(directory_path, ext.upper() + "_Files")
            os.makedirs(folder, exist_ok=True)
            new_path = os.path.join(folder, filename)
            if not os.path.exists(new_path):
                shutil.move(full_path, new_path)
                organized_count += 1
                
        return True, f"Organized {organized_count} files."
    except Exception as e:
        return False, str(e)


def create_item(directory, name, is_folder):
    new_path = os.path.join(directory, name)
    try:
        if is_folder:
            os.makedirs(new_path, exist_ok=True)
        else:
            with open(new_path, 'a'):
                pass
        return True, None
    except Exception as e:
        return False, str(e)

def copy_item(source_path, destination_dir):
    try:
        import shutil
        name = os.path.basename(source_path)
        dest_path = os.path.join(destination_dir, name)
        
        # Handle duplicate naming
        base, ext = os.path.splitext(name)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(destination_dir, f"{base} ({counter}){ext}")
            counter += 1
            
        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path)
        else:
            shutil.copy2(source_path, dest_path)
        return True, None
    except Exception as e:
        return False, str(e)


# ==========================================
# 2. FLASK WEB SERVER API
# ==========================================

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def get_user_folder(home, folder_name):
    std_path = os.path.join(home, folder_name)
    if os.path.exists(std_path):
        return std_path
    onedrive_path = os.path.join(home, "OneDrive", folder_name)
    if os.path.exists(onedrive_path):
        return onedrive_path
    return std_path

@app.route('/api/drives', methods=['GET'])
def api_drives():
    drives = get_local_drives()
    home = os.path.expanduser("~")
    desktop = get_user_folder(home, "Desktop")
    documents = get_user_folder(home, "Documents")
    downloads = get_user_folder(home, "Downloads")
    pictures = get_user_folder(home, "Pictures")
    videos = get_user_folder(home, "Videos")
    return jsonify({
        "drives": drives,
        "home": home,
        "desktop": desktop,
        "documents": documents,
        "downloads": downloads,
        "pictures": pictures,
        "videos": videos
    })

@app.route('/api/files', methods=['GET'])
def api_files():
    path = request.args.get('path')
    if not path or not os.path.exists(path) or not os.path.isdir(path):
         return jsonify({"error": "Invalid path"}), 400
         
    contents, err = get_directory_contents(path)
    if err:
        return jsonify({"error": err}), 500
        
    parent_path = os.path.dirname(path) if path != os.path.dirname(path) else None
    return jsonify({"current_path": path, "parent_path": parent_path, "contents": contents})

@app.route('/api/open', methods=['POST'])
def api_open():
    path = request.json.get('path')
    if not path or not os.path.exists(path):
        return jsonify({"error": "File missing"}), 400
        
    success, err = open_file(path)
    return jsonify({"success": True}) if success else (jsonify({"error": err}), 500)

@app.route('/api/rename', methods=['POST'])
def api_rename():
    data = request.json
    success, err = rename_item(data.get('path'), data.get('new_name'))
    return jsonify({"success": True}) if success else (jsonify({"error": err}), 500)

@app.route('/api/organize', methods=['POST'])
def api_organize():
    success, err = organize_files_by_extension(request.json.get('path'))
    return jsonify({"success": True, "message": err}) if success else (jsonify({"error": err}), 500)

@app.route('/api/create', methods=['POST'])
def api_create():
    data = request.json
    success, err = create_item(data.get('path'), data.get('name'), data.get('is_folder', False))
    return jsonify({"success": True}) if success else (jsonify({"error": err}), 500)

@app.route('/api/paste', methods=['POST'])
def api_paste():
    data = request.json
    success, err = copy_item(data.get('source_path'), data.get('destination_dir'))
    return jsonify({"success": True}) if success else (jsonify({"error": err}), 500)


# ==========================================
# 3. PYWEBVIEW APP LAUNCHER
# ==========================================

def start_flask(port):
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    PORT = 5050
    # Start Flask gently in background
    threading.Thread(target=start_flask, args=(PORT,), daemon=True).start()
    
    # Launch Native App UI
    webview.create_window(
        title="Golden File Explorer",
        url=f"http://localhost:{PORT}",
        width=1100,
        height=700,
        min_size=(800, 500),
        background_color="#121212"
    )
    webview.start()
