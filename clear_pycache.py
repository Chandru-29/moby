import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

def clear_pycache(root: Path):
    for pycache in root.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache)
            print(f"🧹 Deleted: {pycache}")
        except Exception as e:
            print(f"⚠️ Failed to delete {pycache}: {e}")

if __name__ == "__main__":
    print("🔄 Clearing __pycache__ directories...")
    clear_pycache(PROJECT_ROOT)
    print("✅ Done.")
