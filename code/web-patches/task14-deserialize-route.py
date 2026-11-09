import json
import base64

@app.route('/deserialize', methods=['POST'])
def deserialize():
    serialized_data = request.form['data']
    try:
        # CHANGED: parse Base64-encoded JSON without executing pickle opcodes.
        obj = json.loads(base64.b64decode(serialized_data))
        return f"Deserialized object: {obj}"
    except Exception as e:
        return f"Error during deserialization: {str(e)}"
