import urllib.request
import urllib.parse
import base64
import re

# اعداد بالانویس انگلیسی برای شماره‌گذاری زیبا
SUPERSCRIPT_DIGITS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
}

def to_superscript(num):
    return ''.join(SUPERSCRIPT_DIGITS.get(char, char) for char in str(num))

SUB_URL = "https://opti.testspeedpro.ir/vlessagg/sub/6MLH-W6rfyxoUgC0JKu6dZmTGYdx4yE5"

def fetch_and_process():
    req = urllib.request.Request(SUB_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"Error fetching subscription: {e}")
        return

    # بررسی و دکود در صورت Base64 بودن کل ساب
    if not any(content.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://', 'hysteria2://']):
        try:
            content = base64.b64decode(content).decode('utf-8').strip()
        except Exception:
            pass

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    processed_configs = []

    for idx, line in enumerate(lines, start=1):
        superscript_num = to_superscript(idx)
        new_name = f"@Configvibes {superscript_num}🐬"
        encoded_name = urllib.parse.quote(new_name)

        # جایگزینی نام کانفیگ بعد از هشتگ #
        if '#' in line:
            base_part = line.split('#')[0]
            new_line = f"{base_part}#{encoded_name}"
        else:
            new_line = f"{line}#{encoded_name}"

        processed_configs.append(new_line)

    # تبدیل خروجی نهایی به Base64 جهت استاندارد بودن ساب
    final_plain = "\n".join(processed_configs)
    final_base64 = base64.b64encode(final_plain.encode('utf-8')).decode('utf-8')

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(final_base64)

    print(f"Successfully processed {len(processed_configs)} configs.")

if __name__ == "__main__":
    fetch_and_process()
