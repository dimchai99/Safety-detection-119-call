import hmac, hashlib

def verify_signature(raw: bytes, signature: str | None, secret: str) -> bool:
    if not signature:
        return False
    sig = signature.split("=", 1)[-1] if "=" in signature else signature
    mac = hmac.new(secret.encode(), msg=raw, digestmod=hashlib.sha1).hexdigest()
    return hmac.compare_digest(mac, sig)
