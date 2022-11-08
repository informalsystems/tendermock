import json
import requests

test_tx = bytes("\n\x8e\x01\n\x8b\x01\n\x1c/cosmos.bank.v1beta1.MsgSend\x12k\n-cosmos153rpdnp3jcq4kpac8njlyf4gmf724hm6repu72\x12-cosmos1x63y2p7wzsyf9ln0at56vdpe3x66jaf9qzh86t\x1a\x0b\n\x05stake\x12\x0250\x12V\nN\nF\n\x1f/cosmos.crypto.secp256k1.PubKey\x12#\n!\x02'\x11\x08]\xb0\x91z<\xd85v\xe5OR\xc5\xefM\xa6{pb#\\),\t[\x07|8\xd6\xa1\x12\x04\n\x02\x08\x01\x12\x04\x10\xc0\x9a\x0c\x1a@\xfa!'v\xa1T\xac\xd4\xe5\xe0\x19\xefL\x0f\xf0\t\xb0\x94\xbfk^m\x0f\xa72\x84\xb1\xdaeY\x95\xbd_\x16c\xdf3NZ\x0f\xf6v\xad\xc8\xa8\xbbFE\xe8Y\x06\x9f\xa7\xf9\x14\x8f\x8e]\xaf\x01\xb3\x1dH\x92", encoding="utf8").decode()


url = "http://localhost:9999"

# Example echo method
payload = {
    "jsonrpc": "2.0",
    "method": "broadcast_tx_async",
    "params": ["tx"],
    "id": 0,
}
response = requests.post(url, json=payload).json()
print(response)
