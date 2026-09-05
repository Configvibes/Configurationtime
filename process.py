import urllib.request
import urllib.parse
import base64
import ssl

SUPERSCRIPT_DIGITS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
}

def to_superscript(num):
    return ''.join(SUPERSCRIPT_DIGITS.get(char, char) for char in str(num))

SUB_URL = "https://opti.testspeedpro.ir/vlessagg/sub/6MLH-W6rfyxoUgC0JKu6dZmTGYdx4yE5"

def fetch_and_process():
    # ساخت هدرهای مشابه مرورگر برای جلوگیری از بلاک شدن توسط سرور
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*'
    }
    
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(SUB_URL, headers=headers)
    try:
        with urllib.request.urlopen(req, context=context, timeout=15) as response:
            raw_content = response.read().decode('utf-8', errors='ignore').strip()
    except Exception as e:
        print(f"Error fetching subscription: {e}")
        return

    # بررسی اگر کل لینک Base64 انکود شده است
    content = raw_content
    if not any(raw_content.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://', 'hysteria2://', 'tuic://']):
        try:
            # اضافه کردن padding در صورت نیاز
            padded_content = raw_content + '=' * (-len(raw_content) % 4)
            decoded = base64.b64decode(padded_content).decode('utf-8', errors='ignore').strip()
            if decoded:
                content = decoded
        except Exception as e:
            print(f"Base64 decode info: {e}")

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    # اگر هنوز در یک خط است، سعی کنیم بر اساس پروتکل‌ها تقسیم کنیم
    if len(lines) == 1 and not lines[0].startswith('vless://'):
        for proto in ['vless://', 'vmess://', 'trojan://', 'ss://', 'hysteria2://']:
            lines[0] = lines[0].replace(proto, f"\n{proto}")
        lines = [line.strip() for line in lines[0].splitlines() if line.strip()]

    processed_configs = []

    for idx, line in enumerate(lines, start=1):
        if not any(line.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://', 'hysteria2://', 'tuic://']):
            continue

        superscript_num = to_superscript(idx)
        new_name = f"@Configvibes {superscript_num}🐬"
        encoded_name = urllib.parse.quote(new_name)

        if '#' in line:
            base_part = line.split('#')[0]
            new_line = f"{base_part}#{encoded_name}"
        else:
            new_line = f"{line}#{encoded_name}"

        processed_configs.append(new_line)

    print(f"Total configs found: {len(processed_configs)}")

    if not processed_configs:
        print("Warning: No valid configs extracted!")
        return

    # تبدیل خروجی نهایی به Base64
    final_plain = "\n".join(processed_configs)
    final_base64 = base64.b64encode(final_plain.encode('utf-8')).decode('utf-8')

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_base64)

    print("sub.txt updated successfully!")

if __name__ == "__main__":
    fetch_and_process()
