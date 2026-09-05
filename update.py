import base64
import json
import socket
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def fetch_configs(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode("utf-8").strip()
            try:
                decoded = base64.b64decode(content).decode("utf-8")
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
        print(f"Error fetching sub: {e}")
        return []


def parse_host_port(config):
    try:
        if "://" not in config:
            return None, None

        proto, rest = config.split("://", 1)

        if proto in ["vless", "trojan"]:
            main_part = rest.split("#")[0].split("?")[0]
            if "@" in main_part:
                host_port = main_part.split("@")[1]
            else:
                host_port = main_part

            if "]" in host_port:
                host = host_port.split("]")[0] + "]"
                port = int(host_port.split("]:")[1].split("/")[0])
            else:
                host, port = host_port.split(":")
                port = int(port.split("/")[0])
            return host, port

        elif proto == "ss":
            main_part = rest.split("#")[0].split("?")[0].split("/")[0]
            if "@" in main_part:
                host_port = main_part.split("@")[1]
                host, port = host_port.split(":")
                return host, int(port)

        elif proto == "vmess":
            b64_str = rest.split("#")[0]
            missing_padding = len(b64_str) % 4
            if missing_padding:
                b64_str += "=" * (4 - missing_padding)
            decoded = base64.b64decode(b64_str).decode("utf-8")
            data = json.loads(decoded)
            return data.get("add"), int(data.get("port", 443))

    except Exception:
        pass
    return None, None


def quick_check(config):
    """تست سریع بدون فیلتر کردن زودهنگام کانفیگ‌های CDN"""
    host, port = parse_host_port(config)
    if not host or not port:
        return config

    try:
        clean_host = host.replace("[", "").replace("]", "")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((clean_host, int(port)))
        s.close()
        return config
    except Exception:
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
            decoded = base64.b64decode(b64_str).decode("utf-8")
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
    print(f"Total fetched from source: {len(raw_configs)}")

    working_configs = []

    if raw_configs:
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(quick_check, cfg) for cfg in raw_configs]
            for future in as_completed(futures):
                res = future.result()
                if res and res not in working_configs:
                    working_configs.append(res)
                    if len(working_configs) >= 30:
                        break

        # پشتیبان: اگر پینگ گیت‌هاب بستگی داشت، از کانفیگ‌های خام سورس استفاده کن تا لینک خالی نماند
        if len(working_configs) < 30:
            for cfg in raw_configs:
                if cfg not in working_configs:
                    working_configs.append(cfg)
                if len(working_configs) >= 30:
                    break

    print(f"Final selected configs: {len(working_configs)}")

    final_configs = []
    for idx, cfg in enumerate(working_configs[:30], start=1):
        final_configs.append(rename_config(cfg, idx))

    output_data = "\n".join(final_configs)
    b64_output = base64.b64encode(output_data.encode("utf-8")).decode("utf-8")

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(b64_output)


if __name__ == "__main__":
    main()
