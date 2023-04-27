from crypt import methods
from flask import Flask, jsonify, request
from datetime import datetime
import sqlite3

DATABASE_PATH = "./database.db" # Path relative to bootstrap.sh

## Initialization
# Initialize database (open if exists, create if not)
con = sqlite3.connect(DATABASE_PATH)
cur = con.cursor()

# If table doesn't exist (db was created in previous step)
if cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='apps'").fetchall() == []:
    # Create table
    cur.execute("CREATE TABLE apps(name, version, last_updated)")

# Close db
con.close()

# Start app
app = Flask(__name__)

## Helper functions
# Compare two A.B.C version numbers supplied in string format
def isMoreRecentVersion(candidate, reference):
    tmp = candidate.split(".")
    c_major = int(tmp[0])
    c_minor = int(tmp[1])
    c_fix   = int(tmp[2])

    tmp = reference.split(".")
    r_major = int(tmp[0])
    r_minor = int(tmp[1])
    r_fix   = int(tmp[2])

    if c_major > r_major:
        return True
    elif c_major < r_major:
        return False
    else:
        if c_minor > r_minor:
            return True
        elif c_minor < r_minor:
            return False
        else:
            if c_fix > r_fix:
                return True
            else:
                return False


# Return current time as 'YYYY-MM-DD HH:MM:SS'
def getCurrentDateTimeString():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

## Routes
# Return all entries in the database
@app.route("/all", methods=['GET'])
def returnAll():
    # Open db connection
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    # Fetch and iterate over all data
    data = []
    for row in cur.execute("SELECT name, version, last_updated FROM apps"):
        data.append({'name': row[0], 'version': row[1], 'last_updated': row[2]})

    # Close db connection
    con.close()

    return jsonify(data) # 200

# Check if indicated app has a newer version or not
@app.route("/", methods=['GET'])
def hasNewer():
    # Open db connection
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    # Check incoming data
    if "name" in request.args:
        name = request.args["name"]
    else:
        return "Missing argument: name", 400
    
    if "version" in request.args:
        version = request.args["version"]
    else:
        return "Missing argument: version", 400

    # Check if queried app is in database
    cur.execute("SELECT name, version FROM apps WHERE name=?", (name,))
    res = cur.fetchone()
    if res is None:
        return "Unknown name: " + name, 400
    
    # Check if the tracked version for the queried app is more newer than the supplied version
    if isMoreRecentVersion(res[1], version):
        return "True", 200
    else:
        return "False", 200

# Add or update database entry
@app.route("/", methods=['POST'])
def addNew():
    # Open db connection
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    # Prepare new entry info
    if "name" in request.args:
        name = request.args["name"]
    else:
        return "Missing argument: name", 400
    
    if "version" in request.args:
        version = request.args["version"]
    else:
        return "Missing argument: version", 400

    last_updated = getCurrentDateTimeString()

    # Check if an entry with that name already exists
    cur.execute("SELECT name, version FROM apps WHERE name=?", (name,))
    res = cur.fetchone()
    if res:
        # If an entry exists, check if supplied version is more recent than the currently tracked one
        if(isMoreRecentVersion(version, res[1])):
            cur.execute("UPDATE apps SET version=? WHERE name=?", (version, name))
            con.commit()
            con.close()
            return jsonify(name=name, version=version, last_updated=last_updated), 204
        else:
            con.close()
            return "Tracked version " + res[1] + " is more recent than " + version, 400
    else:
        cur.execute("INSERT INTO apps VALUES (?, ?, ?)", (name, version, last_updated))
        con.commit()
        con.close()

        return jsonify(name=name, version=version, last_updated=last_updated), 201
