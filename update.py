import base64
import json
import urllib.parse
import urllib.request

SUB_URL = "https://opti.testspeedpro.ir/vlessagg/sub/6MLH-W6rfyxoUgC0JKu6dZmTGYdx4yE5"


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


def decode_base64_recursively(data_str):
    """دکود کردن لایه‌ای base64 برای استخراج کانفیگ‌های مخفی"""
    data_str = data_str.strip()
    for _ in range(3):
        try:
            missing_padding = len(data_str) % 4
            if missing_padding:
                data_str += "=" * (4 - missing_padding)
            decoded = base64.b64decode(data_str).decode(
                "utf-8", errors="ignore"
            )
            if any(
                proto in decoded
                for proto in ["vless://", "vmess://", "trojan://", "ss://"]
            ):
                data_str = decoded
            else:
                break
        except Exception:
            break
    return data_str


def fetch_raw_sub(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_data = (
                response.read().decode("utf-8", errors="ignore").strip()
            )
            decoded_data = decode_base64_recursively(raw_data)
            lines = [
                line.strip()
                for line in decoded_data.splitlines()
                if line.strip()
            ]
            return lines
    except Exception as e:
        print(f"Error fetching source: {e}")
        return []


def rename_config(config, index):
    num_str = to_superscript(index)
    new_name = f"@Configvibes{num_str}🐬"
    encoded_name = urllib.parse.quote(new_name)

    # تغییر اسم در vmess
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

    # تغییر اسم در vless / trojan / ss / hy2
    if "#" in config:
        base_url = config.split("#")[0]
        return f"{base_url}#{encoded_name}"
    else:
        return f"{config}#{encoded_name}"


def main():
    print("Fetching exact source configs...")
    lines = fetch_raw_sub(SUB_URL)

    # استخراج دقیق تمام کانفیگ‌های سورس شما
    extracted_configs = []
    for line in lines:
        if any(
            line.startswith(proto)
            for proto in [
                "vless://",
                "vmess://",
                "trojan://",
                "ss://",
                "hysteria2://",
                "hy2://",
                "tuic://",
            ]
        ):
            extracted_configs.append(line)

    print(
        f"Total actual configs extracted from YektaCloud sub: {len(extracted_configs)}"
    )

    # تغییر اسم تمام کانفیگ‌ها به @Configvibes
    final_configs = [
        rename_config(cfg, idx)
        for idx, cfg in enumerate(extracted_configs, start=1)
    ]

    if final_configs:
        output_data = "\n".join(final_configs)
        b64_output = base64.b64encode(output_data.encode("utf-8")).decode(
            "utf-8"
        )
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(b64_output)
        print(
            f"Successfully saved all {len(final_configs)} configs to sub.txt!"
        )
    else:
        print("ERROR: Could not extract configs from source!")


if __name__ == "__main__":
    main()
