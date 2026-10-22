"""환경 판별과 Ollama 준비·호출. 모델 호출은 이 모듈에서만 한다."""

import shutil
import subprocess
import sys
import time

import requests

OLLAMA_URL = "http://localhost:11434"
IS_COLAB = "google.colab" in sys.modules
# Colab에서 9B가 돌지 않으면 여기서 직접 "qwen3.5:4b"로 바꾼다 (자동 전환 없음).
MODEL = "qwen3.5:9b" if IS_COLAB else "qwen3.5:4b"

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
