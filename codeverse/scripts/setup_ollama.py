import subprocess
import time
import os
from dotenv import load_dotenv

load_dotenv()

def setup_ollama():
    model = os.getenv('OLLAMA_MODEL', 'codellama')
    
    print("Setting up Ollama...")
    
    # Kill any existing Ollama process
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], 
                      capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # Start Ollama
    try:
        print("Starting Ollama...")
        subprocess.Popen(['ollama', 'serve'], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(5)
        
        # Pull the model
        print(f"Pulling model {model}...")
        result = subprocess.run(['ollama', 'pull', model], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print(f"Successfully pulled model {model}")
            return True
        else:
            print(f"Error pulling model: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error setting up Ollama: {e}")
        return False

if __name__ == "__main__":
    setup_ollama() 