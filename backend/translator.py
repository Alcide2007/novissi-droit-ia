try:
    import httpx
except ImportError:
    httpx = None

try:
    import requests
except ImportError:
    requests = None

import urllib.parse
import urllib.request
import json

def _gtx_translate_chunk(text: str, src: str = "fr", dest: str = "ee") -> str:
    """Traduit un segment court via Google GTX sans dépendance externe obligatoire."""
    clean = text.strip()
    if not clean:
        return text
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={src}&tl={dest}&dt=t&q={urllib.parse.quote(clean)}"
    )

    raw_text = ""
    if httpx is not None:
        try:
            r = httpx.get(url, timeout=6.0)
            if r.status_code == 200:
                raw_text = r.text
        except Exception:
            pass

    if not raw_text and requests is not None:
        try:
            r = requests.get(url, timeout=6.0)
            if r.status_code == 200:
                raw_text = r.text
        except Exception:
            pass

    if not raw_text:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                if resp.status == 200:
                    raw_text = resp.read().decode("utf-8", errors="replace")
        except Exception:
            pass

    if raw_text:
        try:
            data = json.loads(raw_text)
            if isinstance(data, list) and data and isinstance(data[0], list):
                out = "".join(seg[0] for seg in data[0] if seg and seg[0])
                return dedupe_repetitions(out)
        except Exception:
            pass

    return text