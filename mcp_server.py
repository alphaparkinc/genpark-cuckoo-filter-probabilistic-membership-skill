"""MCP Server for GenPark Cuckoo Filter.
100% Python Standard Library.
"""

import json
import sys
from client import CuckooFilter

cf = CuckooFilter(capacity=2000)

def handle_request(req):
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "filter_insert",
                        "description": "Insert an item into the Cuckoo Filter",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"item": {"type": "string"}},
                            "required": ["item"]
                        }
                    },
                    {
                        "name": "filter_contains",
                        "description": "Check if an item exists in the Cuckoo Filter",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"item": {"type": "string"}},
                            "required": ["item"]
                        }
                    },
                    {
                        "name": "filter_delete",
                        "description": "Delete an item from the Cuckoo Filter",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"item": {"type": "string"}},
                            "required": ["item"]
                        }
                    },
                    {
                        "name": "filter_stats",
                        "description": "Retrieve current filter load factor and bucket metrics",
                        "inputSchema": {"type": "object"}
                    }
                ]
            }
        }
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "filter_insert":
            it = args.get("item", "")
            ok = cf.insert(it)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"inserted": ok})}]}
            }
        elif name == "filter_contains":
            it = args.get("item", "")
            exists = cf.contains(it)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"exists": exists})}]}
            }
        elif name == "filter_delete":
            it = args.get("item", "")
            del_ok = cf.delete(it)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"deleted": del_ok})}]}
            }
        elif name == "filter_stats":
            stats = cf.get_stats()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(stats, indent=2)}]}
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
