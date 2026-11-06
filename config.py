import json
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    api_version: str
    timeout_seconds: int = 30
    max_retries: int = 2

    @classmethod
    def load(cls, filename):
        data = json.loads(Path(filename).read_text(encoding="utf-8-sig"))
        version = data.get("api_version", "")
        if not isinstance(version, str) or not re.fullmatch(r"v[0-9]+\.0", version):
            raise ValueError("Điền api_version được hỗ trợ trong Meta App Dashboard, ví dụ định dạng vNN.0.")
        timeout = data.get("timeout_seconds", 30)
        retries = data.get("max_retries", 2)
        if type(timeout) is not int or not 1 <= timeout <= 120:
            raise ValueError("timeout_seconds phải từ 1 đến 120.")
        if type(retries) is not int or not 0 <= retries <= 5:
            raise ValueError("max_retries phải từ 0 đến 5.")
        return cls(version, timeout, retries)
