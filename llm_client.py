"""환경 판별과 Ollama 준비·호출. 모델 호출은 이 모듈에서만 한다."""

import shutil
import subprocess
import sys
import time
from dataclasses import dataclass

import requests

OLLAMA_URL = "http://localhost:11434"
IS_COLAB = "google.colab" in sys.modules
# Colab에서 9B가 돌지 않으면 여기서 직접 "qwen3.5:4b"로 바꾼다 (자동 전환 없음).
MODEL = "qwen3.5:9b" if IS_COLAB else "qwen3.5:4b"

NUM_CTX = 16384
# 연결은 빨리 실패하게, 응답은 CPU에서 느릴 수 있어 넉넉히 기다린다 (초).
CHAT_TIMEOUT = (5, 600)

# 명세 4.1절 응답 형식. 지시 문구는 prompt.md에만 두므로 description은 넣지 않는다.
_FLAG_KEYS = (
    "type",
    "source_span",
    "translation_span",
    "issue",
    "suggestion",
    "guideline_reference",
)
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "flags": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {k: {"type": "string"} for k in _FLAG_KEYS},
                "required": list(_FLAG_KEYS),
            },
        },
        "recommended_grade": {"type": "string"},
    },
    "required": ["flags", "recommended_grade"],
}

# Ollama 설치 스크립트는 zstd가 있어야 하고, GPU 감지에 lspci(pciutils)를 쓴다.
_COLAB_INSTALL = (
    "apt-get update -qq && apt-get install -y -qq zstd pciutils > /dev/null"
    " && curl -fsSL https://ollama.com/install.sh | sh"
)


def _installed_models():
    resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
    resp.raise_for_status()
    return {m["name"] for m in resp.json().get("models", [])}


def _server_up():
    try:
        _installed_models()
        return True
    except requests.RequestException:
        return False


def check():
    """Ollama 연결과 모델 설치를 확인한다. 정상이면 None, 문제가 있으면 원인 문장."""
    try:
        models = _installed_models()
    except requests.RequestException as e:
        return f"Ollama에 연결할 수 없습니다 ({OLLAMA_URL}). Ollama가 실행 중인지 확인하세요. ({e})"
    if MODEL not in models:
        return f"모델 {MODEL}이(가) 없습니다. `ollama pull {MODEL}`로 설치하세요."
    return None


def _prepare_colab():
    if shutil.which("ollama") is None:
        print("Ollama 설치 중...")
        subprocess.run(["bash", "-o", "pipefail", "-c", _COLAB_INSTALL], check=True)

    if not _server_up():
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        for _ in range(30):
            if _server_up():
                break
            time.sleep(1)
        else:
            raise RuntimeError("Ollama 서버가 30초 안에 시작되지 않았습니다.")

    if MODEL not in _installed_models():
        print(f"{MODEL} 다운로드 중 (몇 분 걸립니다)...")
        resp = requests.post(
            f"{OLLAMA_URL}/api/pull", json={"model": MODEL, "stream": False}, timeout=None
        )
        resp.raise_for_status()


def prepare():
    """노트북 첫 셀에서 호출한다. Colab이면 Ollama 설치·실행·모델 다운로드, 로컬이면 확인만."""
    if IS_COLAB:
        _prepare_colab()
    problem = check()
    if problem:
        raise RuntimeError(problem)
    print(f"준비 완료: {'Colab' if IS_COLAB else '로컬'} / 모델 {MODEL}")


@dataclass
class ChatResult:
    content: str  # 모델 응답 원문
    seconds: float  # 요청부터 응답까지 걸린 시간
    prompt_eval_count: int | None  # 입력 토큰 수 (Ollama가 주지 않으면 None)


def chat(messages, schema=RESPONSE_SCHEMA):
    """/api/chat을 한 번 호출한다. schema가 None이면 출력 형식을 지정하지 않는다.

    연결·HTTP 오류는 원인 문장을 담은 RuntimeError로 올린다.
    """
    body = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_ctx": NUM_CTX},
    }
    if schema is not None:
        body["format"] = schema

    start = time.perf_counter()
    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=CHAT_TIMEOUT)
    except requests.ConnectionError as e:
        raise RuntimeError(
            f"Ollama에 연결할 수 없습니다 ({OLLAMA_URL}). Ollama가 실행 중인지 확인하세요. ({e})"
        ) from e
    except requests.Timeout as e:
        raise RuntimeError(f"Ollama 응답이 {CHAT_TIMEOUT[1]}초 안에 오지 않았습니다.") from e
    seconds = time.perf_counter() - start

    if not resp.ok:
        try:
            detail = resp.json().get("error", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"Ollama 오류 (HTTP {resp.status_code}): {detail}")

    data = resp.json()
    return ChatResult(
        content=data["message"]["content"],
        seconds=round(seconds, 2),
        prompt_eval_count=data.get("prompt_eval_count"),
    )
