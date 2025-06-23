from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db_connection, initialize_db
import requests
import os

app = Flask(__name__)
CORS(app)

initialize_db()

# Initialize the database and create the journal_entries table if it doesn't exist
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Daily Journal API!"})

# Endpoint to get all journal entries
# Returns a list of all entries in descending order by creation date
@app.route('/api/journal', methods=['GET'])
def get_entries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM journal_entries ORDER BY created_at DESC')
    entries = cursor.fetchall()
    conn.close()

    if not entries:
        print("No entries found.")
        return jsonify([]), 200  # Or return a message if preferred

    print(f"Fetched {len(entries)} entries.")
    return jsonify([dict(entry) for entry in entries]), 200

# Endpoint to create a new journal entry
# Expects a JSON payload with 'date', 'mood', and 'entry' fields
@app.route('/api/journal', methods=['POST'])
def create_entry():
    data = request.get_json()
    if not data or 'date' not in data or 'mood' not in data or 'entry' not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    date = data.get('date')
    mood = data.get('mood')
    entry = data.get('entry')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO journal_entries (date, mood, entry)
        VALUES (?, ?, ?)
    ''', (date, mood, entry))

    conn.commit()
    conn.close()

    return jsonify({"message": "Entry created successfully",
                    "date" : date, "mood" : mood, "entry" : entry}), 201

# Endpoint to get a random quote
# Fetches a random quote from an external API and returns it
@app.route('/api/quote', methods=['GET'])
def get_quote():
    try:
        response = requests.get('https://zenquotes.io/api/today', timeout=5)
        response.raise_for_status()
        quote_data = response.json()
        if isinstance(quote_data, list) and len(quote_data) > 0:
            quote_obj = quote_data[0]
            return jsonify({
                "quote": quote_obj.get("q"),
                "author": quote_obj.get("a")
            }), 200
        else:
            raise ValueError("Unexpected quote API response format")
    except Exception:
        # fallback quote if the API call fails
        print("Failed to fetch quote from API, using fallback quote.")
        return jsonify({
            "quote": "Keep your face always toward the sunshine—and shadows will fall behind you.",
            "author": "Walt Whitman"
        }), 200

# Endpoint to get a specific journal entry by date
@app.route('/api/journal/<date>', methods=['GET'])
def get_entry_by_date(date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM journal_entries WHERE date = ?', (date,))
    entries = cursor.fetchall()
    conn.close()
    if entries:
        return jsonify([dict(e) for e in entries]), 200
    else:
        return jsonify({"error": "No entries found for that date"}), 404


# Endpoint to delete a journal entry by ID
@app.route('/api/journal/<int:id>', methods=['DELETE'])
def delete_entry(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM journal_entries WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Entry deleted successfully"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
