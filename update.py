import base64
import json
import os
import random
import subprocess
import tempfile
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

SUB_URL = "https://opti.testspeedpro.ir/vlessagg/sub/6MLH-W6rfyxoUgC0JKu6dZmTGYdx4yE5"
BACKUP_SUB = "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt"


def to_superscript(number):
    superscript_map = {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
    }
    return "".join(superscript_map.get(char, char) for char in str(number))


def fetch_configs(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            content = response.read().decode("utf-8", errors="ignore").strip()
            try:
                decoded = base64.b64decode(content).decode(
                    "utf-8", errors="ignore"
                )
                lines = [
                    line.strip() for line in decoded.splitlines() if line.strip()
                ]
                if lines:
                    return lines
            except Exception:
                pass
            return [
                line.strip() for line in content.splitlines() if line.strip()
            ]
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return []


def test_real_ping(config, inport):
    """تست واقعی اتصال و پاسخ‌گویی دیتا توسط sing-box"""
    try:
        singbox_config = {
            "log": {"level": "panic"},
            "inbounds": [{
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "127.0.0.1",
                "listen_port": inport,
            }],
            "outbounds": [{
                "type": "urltest",
                "tag": "url-test",
                "outbounds": ["proxy"],
                "url": "https://www.gstatic.com/generate_204",
                "interval": "1m",
                "tolerance": 50,
            }],
        }

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            json.dump(singbox_config, f)
            config_file = f.name

        cmd = [
            "sing-box",
            "urltest",
            "-c",
            config_file,
            "--url",
            "https://www.gstatic.com/generate_204",
        ]
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=3.0
        )

        os.remove(config_file)

        if proc.returncode == 0:
            return config
    except Exception:
        pass
    return None


def rename_config(config, index):
    num_str = to_superscript(index)
    new_name = f"@Configvibes{num_str}🐬"
    encoded_name = urllib.parse.quote(new_name)

    if config.startswith("vmess://"):
        try:
            b64_str = config[8:].split("#")[0]
            missing_padding = len(b64_str) % 4
            if missing_padding:
                b64_str += "=" * (4 - missing_padding)
            decoded = base64.b64decode(b64_str).decode(
                "utf-8", errors="ignore"
            )
            data = json.loads(decoded)
            data["ps"] = new_name
            new_b64 = base64.b64encode(
                json.dumps(data).encode("utf-8")
            ).decode()
            return f"vmess://{new_b64}"
        except Exception:
            return config

    if "#" in config:
        base_url = config.split("#")[0]
        return f"{base_url}#{encoded_name}"
    else:
        return f"{config}#{encoded_name}"


def main():
    print("Fetching raw configs...")
    raw_configs = fetch_configs(SUB_URL)
    if not raw_configs:
        raw_configs = fetch_configs(BACKUP_SUB)

    valid_configs = [
        c
        for c in raw_configs
        if any(
            c.startswith(p)
            for p in ["vless://", "vmess://", "trojan://", "ss://"]
        )
    ]
    print(f"Total raw proxy configs: {len(valid_configs)}")

    working_configs = []

    # تست Real Delay واقعی
    print("Running Real Handshake Ping tests...")
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [
            executor.submit(test_real_ping, cfg, 20000 + idx)
            for idx, cfg in enumerate(valid_configs[:120])
        ]
        for future in as_completed(futures):
            res = future.result()
            if res:
                working_configs.append(res)
                if len(working_configs) >= 30:
                    break

    print(f"Real Ping verified configs count: {len(working_configs)}")

    # اگر تست کمتر از ۳۰ تا داد، باقی‌مانده را بدون افت ساب پر کن
    if len(working_configs) < 30:
        for cfg in valid_configs:
            if cfg not in working_configs:
                working_configs.append(cfg)
            if len(working_configs) >= 30:
                break

    final_configs = [
        rename_config(cfg, idx)
        for idx, cfg in enumerate(working_configs[:30], start=1)
    ]

    output_data = "\n".join(final_configs)
    b64_output = base64.b64encode(output_data.encode("utf-8")).decode("utf-8")

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(b64_output)


if __name__ == "__main__":
    main()
