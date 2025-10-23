from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Serve frontend (HTML in Python string)
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Video Downloader</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 600px;
            text-align: center;
            color: white;
        }
        
        h1 {
            margin-bottom: 20px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .description {
            margin-bottom: 25px;
            font-size: 1.1rem;
            line-height: 1.5;
        }
        
        .input-group {
            display: flex;
            margin-bottom: 25px;
        }
        
        input {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 8px 0 0 8px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 1rem;
        }
        
        input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        input:focus {
            outline: 2px solid #fdbb2d;
        }
        
        button {
            padding: 15px 25px;
            border: none;
            border-radius: 0 8px 8px 0;
            background-color: #4CAF50;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        button:hover {
            background-color: #45a049;
        }
        
        .platforms {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .platform {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            width: 100px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .platform:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-5px);
        }
        
        .platform.active {
            background: rgba(253, 187, 45, 0.3);
            outline: 2px solid #fdbb2d;
        }
        
        .platform-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .options {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            text-align: left;
        }
        
        .options h3 {
            margin-bottom: 15px;
            text-align: center;
        }
        
        .format-options {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .format-option {
            padding: 10px 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .format-option:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .format-option.active {
            background: rgba(253, 187, 45, 0.3);
            outline: 1px solid #fdbb2d;
        }
        
        .quality-options {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .quality-option {
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }
        
        .quality-option:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .quality-option.active {
            background: rgba(253, 187, 45, 0.3);
            outline: 1px solid #fdbb2d;
        }
        
        .download-btn {
            padding: 15px 30px;
            border-radius: 8px;
            background: linear-gradient(to right, #4776E6, #8E54E9);
            font-size: 1.1rem;
            margin-bottom: 20px;
            width: 100%;
        }
        
        .download-btn:disabled {
            background: rgba(255, 255, 255, 0.2);
            cursor: not-allowed;
        }
        
        .download-btn:disabled:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: none;
        }
        
        .history {
            text-align: left;
        }
        
        .history h3 {
            margin-bottom: 15px;
        }
        
        .history-item {
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .history-item-info {
            flex: 1;
        }
        
        .history-item-title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .history-item-url {
            font-size: 0.8rem;
            opacity: 0.8;
        }
        
        .history-item-action {
            padding: 5px 10px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            cursor: pointer;
        }
        
        .footer {
            margin-top: 25px;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        @media (max-width: 600px) {
            .input-group {
                flex-direction: column;
            }
            
            input {
                border-radius: 8px;
                margin-bottom: 10px;
            }
            
            button {
                border-radius: 8px;
            }
            
            .platforms {
                gap: 10px;
            }
            
            .platform {
                width: 80px;
                padding: 10px;
            }
            
            .format-options {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Universal Video Downloader</h1>
        <p class="description">Download videos from YouTube, Facebook, Instagram, Twitter, TikTok, and more</p>
        
        <div class="input-group">
            <input type="text" id="video-url" placeholder="Paste video URL here...">
            <button id="fetch-btn">Fetch Video</button>
        </div>
        
        <div class="platforms">
            <div class="platform active" data-platform="youtube">
                <div class="platform-icon">📺</div>
                <span>YouTube</span>
            </div>
            <div class="platform" data-platform="facebook">
                <div class="platform-icon">👥</div>
                <span>Facebook</span>
            </div>
            <div class="platform" data-platform="instagram">
                <div class="platform-icon">📷</div>
                <span>Instagram</span>
            </div>
            <div class="platform" data-platform="tiktok">
                <div class="platform-icon">🎵</div>
                <span>TikTok</span>
            </div>
            <div class="platform" data-platform="twitter">
                <div class="platform-icon">🐦</div>
                <span>Twitter</span>
            </div>
        </div>
        
        <div class="options">
            <h3>Download Options</h3>
            <div class="format-options">
                <div class="format-option active" data-format="mp4">MP4 Video</div>
                <div class="format-option" data-format="webm">WebM Video</div>
                <div class="format-option" data-format="mp3">MP3 Audio</div>
                <div class="format-option" data-format="m4a">M4A Audio</div>
            </div>
            <div class="quality-options">
                <div class="quality-option active" data-quality="1080">1080p</div>
                <div class="quality-option" data-quality="720">720p</div>
                <div class="quality-option" data-quality="480">480p</div>
                <div class="quality-option" data-quality="360">360p</div>
                <div class="quality-option" data-quality="240">240p</div>
                <div class="quality-option" data-quality="best-audio" style="display: none;">Best Audio</div>
            </div>
        </div>
        
        <button class="download-btn" id="download-btn" disabled>Download</button>
        
        <div class="history">
            <h3>Recent Downloads</h3>
            <div id="history-list">
                <!-- History items will be added here dynamically -->
            </div>
        </div>
        
        <div class="footer">
            <p>Always respect copyright laws and terms of service when downloading videos.</p>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // DOM elements
            const videoUrlInput = document.getElementById('video-url');
            const fetchBtn = document.getElementById('fetch-btn');
            const downloadBtn = document.getElementById('download-btn');
            const platforms = document.querySelectorAll('.platform');
            const formatOptions = document.querySelectorAll('.format-option');
            const qualityOptions = document.querySelectorAll('.quality-option');
            const historyList = document.getElementById('history-list');
            
            let selectedPlatform = 'youtube';
            let selectedFormat = 'mp4';
            let selectedQuality = '1080';
            
            // Platform selection (manual, but will auto-select on fetch)
            platforms.forEach(platform => {
                platform.addEventListener('click', () => {
                    platforms.forEach(p => p.classList.remove('active'));
                    platform.classList.add('active');
                    selectedPlatform = platform.getAttribute('data-platform');
                });
            });
            
            // Function to update quality options based on format
            function updateQualityOptions() {
                const isAudio = ['mp3', 'm4a'].includes(selectedFormat);
                qualityOptions.forEach(opt => {
                    const q = opt.getAttribute('data-quality');
                    if ((isAudio && q === 'best-audio') || (!isAudio && q !== 'best-audio')) {
                        opt.style.display = 'flex';
                    } else {
                        opt.style.display = 'none';
                    }
                });
                
                // Set default active
                const defaultQ = isAudio ? 'best-audio' : '1080';
                qualityOptions.forEach(opt => {
                    if (opt.getAttribute('data-quality') === defaultQ) {
                        opt.classList.add('active');
                    } else {
                        opt.classList.remove('active');
                    }
                });
                selectedQuality = defaultQ;
            }
            
            // Initial update
            updateQualityOptions();
            
            // Format selection
            formatOptions.forEach(option => {
                option.addEventListener('click', () => {
                    formatOptions.forEach(o => o.classList.remove('active'));
                    option.classList.add('active');
                    selectedFormat = option.getAttribute('data-format');
                    updateQualityOptions();
                });
            });
            
            // Quality selection
            qualityOptions.forEach(option => {
                option.addEventListener('click', () => {
                    qualityOptions.forEach(o => o.classList.remove('active'));
                    option.classList.add('active');
                    selectedQuality = option.getAttribute('data-quality');
                });
            });
            
            // Fetch button handler
            fetchBtn.addEventListener('click', () => {
                const url = videoUrlInput.value.trim();
                
                if (!url) {
                    alert('Please enter a video URL');
                    return;
                }
                
                // Validate URL format
                if (!isValidUrl(url)) {
                    alert('Please enter a valid URL');
                    return;
                }
                
                // Fetch video info from backend
                fetchVideoInfo(url);
            });
            
            // Download button handler
            downloadBtn.addEventListener('click', () => {
                const url = videoUrlInput.value.trim();
                
                if (!url) {
                    alert('Please enter a video URL');
                    return;
                }
                
                // Start actual download
                startDownload(url);
            });
            
            // Helper function to validate URL
            function isValidUrl(string) {
                try {
                    new URL(string);
                    return true;
                } catch (_) {
                    return false;
                }
            }
            
            // Fetch video info from backend
            function fetchVideoInfo(url) {
                downloadBtn.textContent = 'Processing...';
                downloadBtn.disabled = true;
                
                fetch('/fetch_info', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err.error });
                    }
                    return response.json();
                })
                .then(data => {
                    downloadBtn.disabled = false;
                    downloadBtn.textContent = 'Download';
                    
                    // Add to history
                    addToHistory(data.title, url);
                    
                    // Auto-select platform based on URL
                    try {
                        const domain = new URL(url).hostname.replace('www.', '');
                        const platformMap = {
                            'youtube.com': 'youtube',
                            'youtu.be': 'youtube',
                            'facebook.com': 'facebook',
                            'fb.com': 'facebook',
                            'instagram.com': 'instagram',
                            'tiktok.com': 'tiktok',
                            'twitter.com': 'twitter',
                            'x.com': 'twitter'
                        };
                        const detectedPlatform = platformMap[domain] || null;
                        if (detectedPlatform) {
                            platforms.forEach(p => {
                                if (p.getAttribute('data-platform') === detectedPlatform) {
                                    p.classList.add('active');
                                } else {
                                    p.classList.remove('active');
                                }
                            });
                            selectedPlatform = detectedPlatform;
                        }
                    } catch (e) {
                        console.error('Could not detect platform');
                    }
                })
                .catch(error => {
                    alert('Error fetching video info: ' + error);
                    downloadBtn.disabled = false;
                    downloadBtn.textContent = 'Download';
                });
            }
            
            // Start download from backend
            function startDownload(url) {
                downloadBtn.textContent = 'Downloading...';
                downloadBtn.disabled = true;
                
                fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: url,
                        format: selectedFormat,
                        quality: selectedQuality
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err.error });
                    }
                    return response.blob();
                })
                .then(blob => {
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = downloadUrl;
                    a.download = `download.${selectedFormat}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(downloadUrl);
                    a.remove();
                    
                    downloadBtn.disabled = false;
                    downloadBtn.textContent = 'Download';
                })
                .catch(error => {
                    alert('Error downloading video: ' + error);
                    downloadBtn.disabled = false;
                    downloadBtn.textContent = 'Download';
                });
            }
            
            // Add item to history
            function addToHistory(title, url) {
                const historyItem = document.createElement('div');
                historyItem.classList.add('history-item');
                historyItem.innerHTML = `
                    <div class="history-item-info">
                        <div class="history-item-title">${title}</div>
                        <div class="history-item-url">${url}</div>
                    </div>
                    <div class="history-item-action">Download Again</div>
                `;
                
                // Add event listener to the "Download Again" button
                historyItem.querySelector('.history-item-action').addEventListener('click', () => {
                    videoUrlInput.value = url;
                    fetchVideoInfo(url);
                });
                
                historyList.insertBefore(historyItem, historyList.firstChild);
            }
        });
    </script>
</body>
</html>
    """

@app.route("/fetch_info", methods=["POST"])
def fetch_info():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({"title": info.get("title", "Unknown Title")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import after_this_request

@app.route("/download", methods=["POST"])
def download_video():
    try:
        data = request.json
        url = data.get("url")
        selected_format = data.get("format", "mp4")
        selected_quality = data.get("quality", "1080")

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        filename = f"{uuid.uuid4()}.{selected_format}"
        filepath = os.path.join(DOWNLOADS_DIR, filename)

        ydl_opts = {
            "outtmpl": filepath,
        }

        if selected_format in ["mp3", "m4a"]:
            ydl_opts["format"] = "bestaudio"
            codec = selected_format
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
                "preferredquality": "192" if codec == "mp3" else "0",
            }]
        else:
            height = selected_quality if selected_quality != "best-audio" else "1080"
            if selected_format == "mp4":
                ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
                ydl_opts["merge_output_format"] = "mp4"
            elif selected_format == "webm":
                ydl_opts["format"] = f"best[height<={height}][ext=webm]"
                ydl_opts["merge_output_format"] = "webm"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)  # ✅ file is deleted safely after response
            except Exception as e:
                print("Cleanup failed:", e)
            return response

        return send_file(filepath, as_attachment=True, download_name=f"download.{selected_format}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)