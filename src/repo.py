import re
import requests

GH = "https://api.github.com/repos/"
HDR = {"User-Agent": "seance-app"}

def fetch_repo(url):
    m = re.search(r"github\.com/([^/]+)/([^/#?]+)", url)
    if not m:
        return None, "That doesn't look like a GitHub repo URL."
    path = f"{m.group(1)}/{m.group(2).removesuffix('.git')}"
    try:
        r = requests.get(GH + path, headers=HDR, timeout=15)
        if r.status_code == 403:
            return None, "GitHub rate limit hit. Wait a few minutes and try again."
        if r.status_code != 200:
            return None, f"GitHub error {r.status_code}."
        info = r.json()
        raw = {**HDR, "Accept": "application/vnd.github.raw+json"}
        rr = requests.get(GH + path + "/readme", headers=raw, timeout=15)
        readme = rr.text[:2500] if rr.status_code == 200 else "(no README)"
        issues = requests.get(GH + path + "/issues?state=open&per_page=10", headers=HDR, timeout=15).json()
        commits = requests.get(GH + path + "/commits?per_page=5", headers=HDR, timeout=15).json()
    except Exception as e:
        return None, f"Network problem: {e}"
    it = "\n".join(f"- #{i['number']}: {i['title']}" for i in issues
                   if isinstance(i, dict) and "number" in i and "pull_request" not in i)
    ct = "\n".join(f"- {c['commit']['author']['date'][:10]}: {c['commit']['message'].splitlines()[0]}"
                   for c in commits if isinstance(c, dict) and "commit" in c)
    return (f"Repo: {info['name']}\nDescription: {info['description']}\n"
            f"Stars: {info['stargazers_count']}, open issues: {info['open_issues_count']}\n"
            f"Last push: {info['pushed_at']}\nREADME:\n{readme}\n"
            f"Open issues:\n{it}\nRecent commits:\n{ct}"), None