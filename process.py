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

def get_content():
    headers = {
        'User-Agent': 'v2rayNG/1.8.5',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # تلاش اول: دانلود مستقیم با User-Agent نرم‌افزارهای کلاینت
    try:
        req = urllib.request.Request(SUB_URL, headers=headers)
        with urllib.request.urlopen(req, context=context, timeout=15) as response:
            res = response.read().decode('utf-8', errors='ignore').strip()
            if res and len(res) > 20:
                print("Successfully fetched via Direct Request")
                return res
    except Exception as e:
        print(f"Direct fetch failed: {e}")

    # تلاش دوم: استفاده از ورکر / پراکسی کمکی برای دور زدن بلاکی آی‌پی گیت‌هاب
    try:
        proxy_url = "https://corsproxy.io/?" + urllib.parse.quote(SUB_URL)
        req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=15) as response:
            res = response.read().decode('utf-8', errors='ignore').strip()
            if res and len(res) > 20:
                print("Successfully fetched via Proxy Service")
                return res
    except Exception as e:
        print(f"Proxy fetch failed: {e}")

    return ""

def fetch_and_process():
    raw_content = get_content()
    
    if not raw_content:
        print("Error: Could not retrieve content from subscription link.")
        return

    content = raw_content
    # بررسی و دکود Base64
    if not any(raw_content.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://', 'hysteria2://', 'tuic://']):
        try:
            padded_content = raw_content + '=' * (-len(raw_content) % 4)
            decoded = base64.b64decode(padded_content).decode('utf-8', errors='ignore').strip()
            if decoded:
                content = decoded
        except Exception as e:
            print(f"Base64 decode error: {e}")

    # جداکردن خطوط
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    # اگر کل کانفیگ‌ها پشت سر هم بدون newLine باشند
    if len(lines) == 1 and not lines[0].startswith('vless://'):
        for proto in ['vless://', 'vmess://', 'trojan://', 'ss://', 'hysteria2://', 'tuic://']:
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

    print(f"Total configs extracted: {len(processed_configs)}")

    if processed_configs:
        final_plain = "\n".join(processed_configs)
        final_base64 = base64.b64encode(final_plain.encode('utf-8')).decode('utf-8')

        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write(final_base64)

        print("sub.txt updated successfully!")

if __name__ == "__main__":
    fetch_and_process()
