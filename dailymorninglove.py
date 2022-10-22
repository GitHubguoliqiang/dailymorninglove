def checkSignature(data):
    signature = data.get('signature')
    timestamp = data.get('timestamp')
    nonce = data.get("nonce")
    if not signature or not timestamp or not nonce:
        return False
    tmp_str = "".join(sorted([TOKEN, timestamp, nonce]))
    tmp_str = hashlib.sha1(tmp_str.encode('UTF-8')).hexdigest()
    if tmp_str == signature:
        return True
    else:
        return False