import os
import subprocess
import json
import re
import time

def run_command(command, cwd=None, retries=3, delay=5):
  
    for attempt in range(retries):
        try:
            result = subprocess.run(command, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError as e:
            print(f"Attempt {attempt + 1} failed: Error running command {command}: {e.stderr.decode().strip()}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    print("Max retries reached. Command failed.")
    return None

def get_driver_info(drivers_path):
    """Retrieve version and git hash information for drivers."""
    driver_info = {}

    for driver in os.listdir(drivers_path):
        if not driver.startswith("indi-"):
            continue

        driver_path = os.path.join(drivers_path, driver)
        if os.path.isdir(driver_path):
            print(f"Processing driver: {driver}")
            version_major = None
            version_minor = None
            version_file = os.path.join(driver_path, "CMakeLists.txt")

            if os.path.exists(version_file):
                try:
                    with open(version_file, 'r') as f:
                        for line in f:
                            major_match = re.search(r'set\s*\(\s*\w*_VERSION_MAJOR\s*([0-9]+)\s*\)', line, re.IGNORECASE)
                            minor_match = re.search(r'set\s*\(\s*\w*_VERSION_MINOR\s*([0-9]+)\s*\)', line, re.IGNORECASE)
                            if major_match:
                                version_major = major_match.group(1)
                            if minor_match:
                                version_minor = minor_match.group(1)
                            if version_major is not None and version_minor is not None:
                                break
                except Exception as e:
                    print(f"Error reading version from {version_file}: {str(e)}")

            version = f"{version_major}.{version_minor}" if version_major is not None and version_minor is not None else "Unknown"
            latest_hash = run_command(["git", "rev-parse", "HEAD"], cwd=drivers_path)

            driver_info[driver] = {
                "version": version,
                "latest_hash": latest_hash
            }
    
    return driver_info

def main():
    repo_url = "https://github.com/indilib/indi-3rdparty"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.join(script_dir, "indi-3rdparty")

    if not os.path.exists(repo_dir):
        print(f"Cloning repository from {repo_url} to {repo_dir}...")
        if not run_command(["git", "clone", "--depth=1", repo_url, repo_dir]):
            print("Failed to clone repository after multiple attempts. Exiting.")
            return

    drivers_path = repo_dir

    driver_info = get_driver_info(drivers_path)

    if driver_info:
        print("Driver information retrieved successfully:")
        print(json.dumps(driver_info, indent=2))
    else:
        print("No driver information found.")

if __name__ == "__main__":
    main()