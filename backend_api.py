import os
from typing import Dict, List, Tuple

import librosa
import numpy as np
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_EXTS = {".wav", ".mp3"}


def infer_label(file_name: str) -> str:
    lower = file_name.lower()
    if "asli" in lower:
        return "asli"
    if "clone" in lower or "cloning" in lower:
        return "cloning"
    return "unknown"


def list_audio_files() -> List[str]:
    roots = [BASE_DIR, os.path.join(BASE_DIR, "dataset")]
    found = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in os.listdir(root):
            path = os.path.join(root, name)
            ext = os.path.splitext(name)[1].lower()
            if os.path.isfile(path) and ext in AUDIO_EXTS:
                found.append(path)
    # Preserve order but avoid duplicates.
    unique = []
    seen = set()
    for p in found:
        if p not in seen:
            unique.append(p)
            seen.add(p)
    return unique


def extract_mfcc_stats(path: str, n_mfcc: int = 13) -> Tuple[np.ndarray, np.ndarray, int, float]:
    y, sr = librosa.load(path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)
    duration = float(len(y) / sr) if sr else 0.0
    return mfcc_mean, mfcc_std, sr, duration


def as_float(v: float) -> float:
    return float(np.round(v, 6))


def build_rows(paths: List[str]) -> List[Dict[str, object]]:
    rows = []
    for path in paths:
        file_name = os.path.basename(path)
        label = infer_label(file_name)
        mfcc_mean, mfcc_std, sr, duration = extract_mfcc_stats(path)

        row: Dict[str, object] = {
            "file": file_name,
            "label": label,
            "sample_rate": int(sr),
            "duration_sec": as_float(duration),
        }

        for i in range(len(mfcc_mean)):
            row[f"mean_{i + 1}"] = as_float(mfcc_mean[i])
            row[f"std_{i + 1}"] = as_float(mfcc_std[i])

        rows.append(row)

    return rows


def numeric_columns(rows: List[Dict[str, object]], headers: List[str]) -> List[str]:
    result = []
    for h in headers:
        valid = 0
        for row in rows:
            v = row.get(h)
            if isinstance(v, (int, float)):
                valid += 1
        if valid > 0:
            result.append(h)
    return result


def build_column_stats(rows: List[Dict[str, object]], headers: List[str]) -> List[Dict[str, object]]:
    stats = []
    for h in numeric_columns(rows, headers):
        vals = [row[h] for row in rows if isinstance(row.get(h), (int, float))]
        if not vals:
            continue
        arr = np.array(vals, dtype=float)
        stats.append(
            {
                "column": h,
                "n": int(len(arr)),
                "mean": as_float(float(np.mean(arr))),
                "std": as_float(float(np.std(arr, ddof=1))) if len(arr) > 1 else 0.0,
                "min": as_float(float(np.min(arr))),
                "max": as_float(float(np.max(arr))),
            }
        )
    return stats


def build_group_profile(rows: List[Dict[str, object]]) -> Dict[str, object]:
    mean_cols = [f"mean_{i}" for i in range(1, 14)]
    groups = {}
    for label in ["asli", "cloning"]:
        group_rows = [r for r in rows if r.get("label") == label]
        if not group_rows:
            continue
        profile = []
        for col in mean_cols:
            vals = [r[col] for r in group_rows if isinstance(r.get(col), (int, float))]
            profile.append(as_float(float(np.mean(vals))) if vals else 0.0)
        groups[label] = {
            "count": len(group_rows),
            "mean_profile": profile,
            "coefficients": [f"MFCC_{i}" for i in range(1, 14)],
        }
    return groups


@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "statistik_mfcc.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/audio-files")
def audio_files():
    paths = list_audio_files()
    payload = []
    for p in paths:
        payload.append(
            {
                "path": p,
                "file": os.path.basename(p),
                "label": infer_label(os.path.basename(p)),
            }
        )
    return jsonify({"items": payload, "count": len(payload)})


@app.route("/api/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return ("", 204)

    payload = request.get_json(silent=True) or {}
    selected = payload.get("files")

    if selected:
        resolved = []
        for rel in selected:
            candidate = os.path.join(BASE_DIR, rel)
            if os.path.isfile(candidate) and os.path.splitext(candidate)[1].lower() in AUDIO_EXTS:
                resolved.append(candidate)
        paths = resolved
    else:
        paths = list_audio_files()

    if not paths:
        return jsonify({"error": "Tidak ada file audio WAV/MP3 ditemukan."}), 400

    rows = build_rows(paths)
    headers = list(rows[0].keys()) if rows else []
    num_cols = numeric_columns(rows, headers)

    response = {
        "headers": headers,
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "column_count": len(headers),
            "numeric_column_count": len(num_cols),
            "missing_count": 0,
        },
        "column_stats": build_column_stats(rows, headers),
        "group_profile": build_group_profile(rows),
    }
    return jsonify(response)


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
