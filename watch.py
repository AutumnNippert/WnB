import os
import sys
import time
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

print("Watch and Backup! - Created by Cardigan")

if len(sys.argv) != 2:
    print("Usage: wnb.exe <folder_name>")
    sys.exit(1)
else:
    path = sys.argv[1]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backup_path = os.path.join(script_dir, "backup")
    log_path = os.path.join(script_dir, "log")

# Ensure the log folder exists
os.makedirs(backup_path, exist_ok=True)
os.makedirs(log_path, exist_ok=True)

# Log file path
log_filename = os.path.join(log_path, "change_log.txt")

def write_to_change_log(event):
    with open(log_filename, "a") as log_file:
        log_file.write(f"{datetime.now()}: {event}\n")

# Function to perform the initial full backup of the folder
def backup(src_folder):
    now = datetime.now()
    #format the time
    dt_string = now.strftime("%Y-%m-%d-%H_%M_%S")
    dst_folder = os.path.join(backup_path, dt_string)
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_folder, os.path.relpath(src_file, src_folder))
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)

        for dir in dirs:
            src_dir = os.path.join(root, dir)
            dst_dir = os.path.join(dst_folder, os.path.relpath(src_dir, src_folder))
            os.makedirs(dst_dir, exist_ok=True)
    
# Perform the initial full backup
backup(path)

# Create a custom event handler that will react to file system events
class BackupHandler(FileSystemEventHandler):
    def on_modified(self, event):
        backup(path)
        write_to_change_log(f"{event.src_path} was modified")

    def on_created(self, event):
        backup(path)
        write_to_change_log(f"{event.src_path} was created")

    def on_deleted(self, event):
        backup(path)
        write_to_change_log(f"{event.src_path} was deleted")

    def on_moved(self, event):
        backup(path)
        write_to_change_log(f"{event.src_path} was moved to {event.dest_path}")

# Create an observer that will watch the folder using our custom event handler
observer = Observer()
event_handler = BackupHandler()
observer.schedule(event_handler, path=path, recursive=True)

# Start the observer
observer.start()

try:
    print(f"Watching for changes in ./{path}")
    # Run the observer indefinitely in a loop
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Stop the observer if the user interrupts the program (e.g., by pressing Ctrl+C)
    observer.stop()

# Wait for the observer's thread to finish
observer.join()