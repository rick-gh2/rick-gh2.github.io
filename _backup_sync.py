import json, subprocess, os, urllib.request, hashlib

BACKUP_DIR = "/home/rickspark/.openclaw/workspace/personal-website-backup"
TOKEN = "REPLACE_ME_WITH_REAL_TOKEN"  # ⚠️ Replace before use!

def github_api(path):
    url = f"https://api.github.com/repos/rick-gh2/rick-gh2.github.io/contents/{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"[ERROR] GitHub API failed for {path}: {e}")
        return None

def backup_file(rel_path):
    full = os.path.join(BACKUP_DIR, rel_path)
    if not os.path.isfile(full):
        print(f"  [SKIP] Not found: {rel_path}")
        return False
    content = open(full).read()
    data = github_api(rel_path)
    sha = data["sha"] if data else None
    encoded = urllib.parse.quote(base64.b64encode(content.encode()).decode())
    payload = {"message": f"backup update: sync {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", "content": encoded}
    if sha:
        payload["sha"] = sha
    url = f"https://api.github.com/repos/rick-gh2/rick-gh2.github.io/contents/{rel_path}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json", "Accept": "application/vnd.github+json"}, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  [OK] Synced: {rel_path}")
            return True
    except Exception as e:
        print(f"  [FAIL] {rel_path}: {e}")
        return False

if __name__ == "__main__":
    import base64, urllib.parse, datetime
    files_to_sync = ["backup_timestamp.txt"]
    new_count = 0
    updated_count = 0
    for f in files_to_sync:
        if backup_file(f):
            # Check if file existed on remote before
            data = github_api(f)
            if data and "sha" in data:
                updated_count += 1
            else:
                new_count += 1
    print(f"\n📦 Backup complete: {new_count} new, {updated_count} updated")
