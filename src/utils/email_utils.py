import re
from html import unescape
from email.utils import getaddresses
from bs4 import BeautifulSoup


def extract_body(msg) -> str:
    """Pull plain-text content out of an email.message.Message, stripping HTML tags."""
    texts = []

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in ("text/plain", "text/html"):
                payload = part.get_payload(decode=True)
                if payload:
                    text = unescape(payload.decode(errors="ignore"))
                    text = BeautifulSoup(text, "html.parser").get_text(" ")
                    texts.append(text)
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            text = unescape(payload.decode(errors="ignore"))
            text = BeautifulSoup(text, "html.parser").get_text(" ")
            texts.append(text)

    clean = " ".join(texts)
    clean = re.sub(r'\\+', ' ', clean)
    clean = re.sub(r'[\r\n\t]+', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def all_recipients(msg) -> str:
    """Collect the unique set of addresses across From/To/Cc/Bcc headers."""
    fields = []
    for header in ("From", "To", "Cc", "Bcc"):
        fields.extend(getaddresses([msg.get(header, "")]))
    return ", ".join(sorted(set(addr for _, addr in fields if addr)))


def clean_text(text):
    """Sanitize text for safe CSV/Excel export (control chars, cell limit, formula injection)."""
    if not isinstance(text, str):
        return text
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F​‌‍‎‏﻿]', '', text)
    text = text.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
    text = text[:32767]
    if text.startswith(("=", "+", "-", "@")):
        text = "'" + text
    return text
