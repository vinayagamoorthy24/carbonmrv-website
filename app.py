from flask import Flask, render_template, request, jsonify, Response
import hashlib
import json
import time

app = Flask(__name__)

# Blockchain Class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block([], previous_hash="1")  # Genesis block

    def create_block(self, credits=None, previous_hash=""):
        if credits is None:
            credits = []

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "credits": credits,
            "previous_hash": previous_hash,
            "nonce": 0
        }

        mined_block = self.proof_of_work(block)
        self.chain.append(mined_block)
        print(f"Block #{mined_block['index']} mined! Nonce: {mined_block['nonce']}, Hash: {mined_block['hash']}")
        return mined_block

    def proof_of_work(self, block, difficulty=4):
        while True:
            blk_copy = block.copy()
            blk_copy.pop("hash", None)
            block_string = json.dumps(blk_copy, sort_keys=True).encode()
            hash_value = hashlib.sha256(block_string).hexdigest()

            if hash_value.startswith("0" * difficulty):
                block["hash"] = hash_value
                return block
            else:
                block["nonce"] += 1

    def get_chain(self):
        return self.chain


# App Initialization
blockchain = Blockchain()


# Routes
@app.route('/')
def dashboard():
    """Main dashboard page (form + chain display)."""
    return render_template("dashboard.html")

@app.route('/add_credit', methods=['POST'])
def add_credit():
    """Add new carbon credit and mine a block."""
    data = request.get_json()
    issuer = data['issuer']
    project = data['project']
    verifier = data['verifier']
    amount = int(data['amount'])
    country = data['country']

    credit = {
        "issuer": issuer,
        "project": project,
        "verifier": verifier,
        "amount": amount,
        "country": country
    }

    last_block = blockchain.get_chain()[-1]
    previous_hash = last_block.get("hash", "")

    new_block = blockchain.create_block([credit], previous_hash)

    return jsonify({
        "message": "Block mined!",
        "nonce": new_block['nonce'],
        "hash": new_block['hash']
    })

@app.route('/chain.json')
def chain_json():
    """Return blockchain as JSON (for frontend auto-refresh)."""
    return jsonify({
        "length": len(blockchain.get_chain()),
        "chain": blockchain.get_chain()
    })

@app.route('/download_chain')
def download_chain():
    """Download blockchain data as a JSON file."""
    chain_data = json.dumps(blockchain.get_chain(), indent=4)
    return Response(
        chain_data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=blockchain.json"}
    )


# Run App
if __name__ == "__main__":
    app.run(debug=True)
