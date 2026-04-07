from pathlib import Path
import sys

# These are the files we specifically built for your Gradio/Offline architecture
REQUIRED_FILES = [
    "README.md",
    "requirements.txt",
    "app.py",
    "demo.py"
]

# These are your core engine folders
REQUIRED_DIRS = [
    "src",
    "assets",
    "tests"
]

OPTIONAL_BUT_RECOMMENDED = [
    ".gitignore",
    "agent.py"
]

def check_exists(path_str):
    return Path(path_str).exists()

def main():
    root = Path(".").resolve()
    print(f"🔍 Checking repository structure at: {root}")

    failed = False

    print("\n[Files]")
    for f in REQUIRED_FILES:
        if check_exists(f):
            print(f"  ✅ OK   {f}")
        else:
            print(f"  ❌ MISS {f}")
            failed = True

    print("\n[Directories]")
    for d in REQUIRED_DIRS:
        if check_exists(d):
            print(f"  ✅ OK   {d}/")
        else:
            print(f"  ❌ MISS {d}/")
            failed = True

    print("\n[Deep Internal Checks]")
    if check_exists("assets/campaign_config.json"):
        print("  ✅ OK   assets/campaign_config.json")
    else:
        print("  ❌ MISS assets/campaign_config.json (Critical for physics engine)")
        failed = True
        
    if check_exists("src/environment.py"):
        print("  ✅ OK   src/environment.py")
    else:
        print("  ❌ MISS src/environment.py")
        failed = True

    print("\n[Basic Content Checks]")
    if Path("requirements.txt").exists():
        reqs = Path("requirements.txt").read_text(encoding="utf-8").strip()
        if not reqs:
            print("  ❌ MISS requirements.txt is empty")
            failed = True
        else:
            print("  ✅ OK   requirements.txt has content")

    if Path("README.md").exists():
        readme = Path("README.md").read_text(encoding="utf-8").strip()
        if not readme:
            print("  ❌ MISS README.md is empty")
            failed = True
        else:
            print("  ✅ OK   README.md has content")

    if failed:
        print("\n🚨 PRECHECK FAILED. Please fix the missing files above.")
        sys.exit(1)

    print("\n🎉 PRECHECK PASSED! Your repository is perfectly structured for the Hackathon.")
    sys.exit(0)

if __name__ == "__main__":
    main()