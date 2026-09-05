import base64
import random
import socket
import urllib.parse
import urllib.request

# لیست ایموجی‌ها برای ترکیب با شماره‌ها
EMOJIS = [
    "🐬",
    "🎀",
    "✨",
    "💫",
    "⚡",
    "🔥",
    "🌟",
    "💎",
    "🔮",
    "🚀",
    "🦄",
    "❄️",
    "🍬",
    "🍒",
    "🍓",
    "🎯",
]

SUB_URL = "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt"


def to_superscript(number):
    """تبدیل عدد معمولی به عدد بالانویس (Superscript)"""
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
    """دانلود و Decode کردن ساب‌سکریپشن"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode("utf-8").strip()
            try:
                decoded = base64.b64decode(content).decode("utf-8")
                return [
                    line.strip() for line in decoded.splitlines() if line.strip()
                ]
            except Exception:
                return [
                    line.strip() for line in content.splitlines() if line.strip()
                ]
    except Exception as e:
        print(f"Error fetching sub: {e}")
        return []


def parse_host_port(config):
    """استخراج Host و Port از کانفیگ‌ها"""
    try:
        if "://" not in config:
            return None, None

        proto, rest = config.split("://", 1)

        if "#" in rest:
            rest = rest.split("#")[0]

        if proto in ["vless", "trojan"]:
            main_part = rest.split("?")[0]
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
            main_part = rest.split("?")[0].split("/")[0]
            if "@" in main_part:
                host_port = main_part.split("@")[1]
                host, port = host_port.split(":")
                return host, int(port)

        elif proto == "vmess":
            import json

            decoded = base64.b64decode(rest).decode("utf-8")
            data = json.loads(decoded)
            return data.get("add"), int(data.get("port", 443))

    except Exception:
        pass
    return None, None


def real_ping(host, port, timeout=2.5):
    """تست پینگ واقعی TCP Connect"""
    if not host or not port:
        return None
    try:
        clean_host = host.replace("[", "").replace("]", "")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((clean_host, int(port)))
        s.close()
        return True
    except Exception:
        return False


def rename_config(config, index):
    """تغییر نام کانفیگ به فرمت @Configvibes¹🐬 تا ⁵⁰"""
    num_str = to_superscript(index)
    emoji = random.choice(EMOJIS)
    new_name = f"@Configvibes{num_str}{emoji}"
    encoded_name = urllib.parse.quote(new_name)

    if config.startswith("vmess://"):
        import json

        try:
            b64_str = config[8:]
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
    print("Fetching configs...")
    raw_configs = fetch_configs(SUB_URL)
    print(f"Total configs received: {len(raw_configs)}")

    working_configs = []

    for cfg in raw_configs:
        host, port = parse_host_port(cfg)
        if host and port:
            if real_ping(host, port):
                count = len(working_configs) + 1
                renamed = rename_config(cfg, count)
                working_configs.append(renamed)
                print(f"[OK] {count}. Connected -> {host}:{port}")
                if len(working_configs) >= 50:
                    break

    print(f"Found {len(working_configs)} active configs.")

    output_data = "\n".join(working_configs)
    b64_output = base64.b64encode(output_data.encode("utf-8")).decode("utf-8")

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(b64_output)


if __name__ == "__main__":
    main()
