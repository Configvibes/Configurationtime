import base64
import json
import urllib.parse
import urllib.request

# لیست لینک‌های سورس (اگر اولی کار نکرد، میرود سراغ بعدی)
SOURCES = [
    "https://opti.testspeedpro.ir/vlessagg/sub/6MLH-W6rfyxoUgC0JKu6dZmTGYdx4yE5",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
]


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


def fetch_configs_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8", errors="ignore").strip()
            # تلاش برای دکود Base64
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

            lines = [
                line.strip() for line in content.splitlines() if line.strip()
            ]
            return lines
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return []


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
    raw_configs = []

    # تست سورس‌ها به ترتیب
    for src in SOURCES:
        print(f"Trying source: {src}")
        fetched = fetch_configs_from_url(src)
        if fetched:
            # فقط کانفیگ‌های معتبر پروکسی را جدا کن
            valid = [
                c
                for c in fetched
                if any(
                    c.startswith(p)
                    for p in ["vless://", "vmess://", "trojan://", "ss://"]
                )
            ]
            if valid:
                print(f"Success! Found {len(valid)} configs from {src}")
                raw_configs.extend(valid)
                if len(raw_configs) >= 30:
                    break

    selected_configs = raw_configs[:30]
    print(f"Total selected configs: {len(selected_configs)}")

    final_configs = [
        rename_config(cfg, idx)
        for idx, cfg in enumerate(selected_configs, start=1)
    ]

    if final_configs:
        output_data = "\n".join(final_configs)
        b64_output = base64.b64encode(output_data.encode("utf-8")).decode(
            "utf-8"
        )
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(b64_output)
        print("sub.txt updated successfully!")
    else:
        print("CRITICAL: No configs found across all sources!")


if __name__ == "__main__":
    main()
