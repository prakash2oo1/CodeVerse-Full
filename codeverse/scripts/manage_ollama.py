import subprocess
import time
import sys
import os
import requests

def check_ollama_running():
    try:
        response = requests.get('http://localhost:11434/api/version')
        return response.status_code == 200
    except:
        return False

def start_ollama():
    if sys.platform == 'win32':
        try:
            # Kill existing Ollama process if any
            subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], 
                         capture_output=True)
            time.sleep(2)
            
            # Start Ollama
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            time.sleep(5)
            
            # Check if model exists
            result = subprocess.run(['ollama', 'list'], 
                                 capture_output=True, text=True)
            
            if 'codellama:13b' not in result.stdout:
                print("Pulling CodeLlama model...")
                subprocess.run(['ollama', 'pull', 'codellama:13b'])
                
        except Exception as e:
            print(f"Error managing Ollama: {e}")
            return False
    return True

if __name__ == "__main__":
    if not check_ollama_running():
        print("Starting Ollama...")
        if start_ollama():
            print("Ollama started successfully")
        else:
            print("Failed to start Ollama")
    else:
        print("Ollama is already running") 