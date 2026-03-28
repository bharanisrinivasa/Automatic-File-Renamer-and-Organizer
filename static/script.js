let currentPath = '';
let selectedFilePath = null;

// DOM Elements
const _drivesList = document.getElementById('drives-list');
const _fileList = document.getElementById('file-list');
const _pathInput = document.getElementById('path-input');
const _upBtn = document.getElementById('up-btn');
const _refreshBtn = document.getElementById('refresh-btn');
const _renameBtn = document.getElementById('rename-btn');
const _organizeBtn = document.getElementById('organize-btn');

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    loadDrives();
    
    // Event Listeners
    _upBtn.addEventListener('click', navigateUp);
    _refreshBtn.addEventListener('click', () => loadFiles(currentPath));
    
    _pathInput.addEventListener('keydown', (e) => {
        if(e.key === 'Enter') loadFiles(_pathInput.value);
    });

    _renameBtn.addEventListener('click', renameSelected);
    _organizeBtn.addEventListener('click', organizeDirectory);
});

// Loading Data
async function loadDrives() {
    try {
        const res = await fetch('/api/drives');
        const data = await res.json();
        
        _drivesList.innerHTML = '';
        
        // Add special directories
        const addSpecialDir = (name, icon, path) => {
            if (!path) return;
            const li = document.createElement('li');
            li.innerHTML = `<i class="${icon}"></i> ${name}`;
            li.onclick = () => loadFiles(path);
            _drivesList.appendChild(li);
        };

        addSpecialDir('Home', 'ph-fill ph-house', data.home);
        addSpecialDir('Desktop', 'ph-fill ph-desktop', data.desktop);
        addSpecialDir('Documents', 'ph-fill ph-file-text', data.documents);
        addSpecialDir('Downloads', 'ph-fill ph-download-simple', data.downloads);
        addSpecialDir('Pictures', 'ph-fill ph-image', data.pictures);
        addSpecialDir('Videos', 'ph-fill ph-video-camera', data.videos);
        
        // Load initial path as home
        if (!currentPath) {
            loadFiles(data.home);
        }
        
        // Add drives
        data.drives.forEach(drive => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="ph-fill ph-hard-drive"></i> ${drive}`;
            li.onclick = () => loadFiles(drive);
            _drivesList.appendChild(li);
        });
        
    } catch (e) {
        console.error("Failed to load drives:", e);
    }
}

async function loadFiles(path) {
    if(!path) return;
    
    _fileList.innerHTML = `<div class="loading-state"><i class="ph ph-spinner ph-spin"></i> Loading...</div>`;
    
    try {
        const res = await fetch(`/api/files?path=${encodeURIComponent(path)}`);
        
        if(!res.ok) {
            const err = await res.json();
            alert("Error: " + err.error);
            _fileList.innerHTML = '';
            return;
        }
        
        const data = await res.json();
        currentPath = data.current_path;
        _pathInput.value = currentPath;
        
        renderFiles(data.contents);
        
    } catch (e) {
        alert("Failed to connect to server.");
        console.error(e);
    }
}

function renderFiles(contents) {
    _fileList.innerHTML = '';
    selectedFilePath = null;
    _renameBtn.disabled = true;
    
    if(contents.length === 0) {
         _fileList.innerHTML = `<div class="loading-state" style="color:var(--text-secondary)">This folder is empty.</div>`;
         return;
    }
    
    contents.forEach(item => {
        const div = document.createElement('div');
        div.className = 'file-item';
        
        const iconClass = item.is_dir ? 'ph-fill ph-folder icon-folder' : 'ph ph-file-text icon-file';
        
        div.innerHTML = `
            <div class="item-name"><i class="${iconClass}"></i> ${item.name}</div>
            <div class="item-date">${item.modified}</div>
            <div class="item-type">${item.type}</div>
            <div class="item-size">${item.size}</div>
        `;
        
        // Click to select
        div.onclick = (e) => {
            document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
            div.classList.add('selected');
            selectedFilePath = item.path;
            _renameBtn.disabled = false;
        };
        
        // Double click to open/navigate
        div.ondblclick = (e) => {
            if(item.is_dir) {
                loadFiles(item.path);
            } else {
                openFile(item.path);
            }
        };
        
        _fileList.appendChild(div);
    });
}

// Navigation Functions
function navigateUp() {
    // If we're at C:\, splitting by \ might just return C:. We can deduce parent logic here, or ask API.
    // Easier: Just ask API to load parent by manipulating string.
    let parent = currentPath.substring(0, currentPath.lastIndexOf('\\'));
    if(!parent.includes('\\') && parent.length >= 2) {
        parent = parent + '\\'; // e.g. C: -> C:\
    }
    if (parent) {
        loadFiles(parent);
    }
}

async function openFile(path) {
    try {
        const res = await fetch('/api/open', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: path})
        });
        if(!res.ok) {
            const err = await res.json();
            alert("Error opening file: " + err.error);
        }
    } catch(e) { console.error(e); }
}

// Action Functions
async function renameSelected() {
    if(!selectedFilePath) return;
    
    // Extract base name
    const oldName = selectedFilePath.split('\\').pop();
    const newName = prompt(`Rename:\n${oldName}`, oldName);
    
    if(newName && newName !== oldName) {
        try {
            const res = await fetch('/api/rename', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: selectedFilePath, new_name: newName})
            });
            if(res.ok) {
                loadFiles(currentPath); // refresh
            } else {
                const err = await res.json();
                alert("Rename failed: " + err.error);
            }
        } catch(e) { console.error(e); }
    }
}

async function organizeDirectory() {
    if(!confirm(`This will group all files in '${currentPath}' into folders based on their extension. Continue?`)) return;
    
    try {
        const res = await fetch('/api/organize', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: currentPath})
        });
        
        const data = await res.json();
        
        if(res.ok) {
            alert("Success: " + data.message);
            loadFiles(currentPath); // refresh
        } else {
            alert("Organize failed: " + data.error);
        }
    } catch(e) { console.error(e); }
}
