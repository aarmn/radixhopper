import os
import sys
import subprocess
import radixhopper

def find_st_path():
    # Get the directory of the radixhopper package
    radixhopper_dir = os.path.dirname(radixhopper.__file__)
    # Construct the path to st.py
    st_path = os.path.join(radixhopper_dir, 'st.py')
    return st_path

def run_streamlit_app():
    st_path = find_st_path()
    
    if not os.path.exists(st_path):
        print(f"Error: {st_path} not found.")
        return

    commands = [
        [sys.executable, '-m', 'streamlit', 'run', st_path],
        ['streamlit', 'run', st_path]
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
            return
        except subprocess.CalledProcessError:
            print(f"Command failed: {' '.join(cmd)}")
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")

    print("All attempts to run Streamlit app failed.")

if __name__ == "__main__":
    run_streamlit_app()