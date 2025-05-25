import os
import traceback

def ensure_output_folder():
    """Ensure the _output folder exists."""
    output_folder = os.path.join(os.getcwd(), '_output')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder

def log_crash(exception):
    """Log crash details to a file in the _output folder."""
    output_folder = ensure_output_folder()
    crash_log_path = os.path.join(output_folder, 'crashlog.txt')
    with open(crash_log_path, 'a') as crash_log:
        crash_log.write("\n--- Crash Log ---\n")
        crash_log.write(traceback.format_exc())
        crash_log.write("\n")
    print(f"Crash log written to {crash_log_path}")
