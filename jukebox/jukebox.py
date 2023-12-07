from flask import Flask, request
import subprocess, os, random, json

app = Flask(__name__)

process = None

@app.route('/jukebox', methods=['GET'])
def handle_get():
    global process
    msg = ""
    if request.method == 'GET':
        command = request.args['command']
        if command == 'start':
            msg+='Jukebox starting\n'
            files = os.listdir('/var/snap/mpg123-core/current')
            mpFiles = []
            for file in files:
                if file.endswith('.mp3'):
                    mpFiles.append(file)
            msg+= 'Files available: %s\n' % mpFiles
            if len(mpFiles):
                if process:
                    msg += "Stopping current music first\n"
                    process.kill()
                #print ("Available interfaces")
                #process = subprocess.Popen(['aplay', '-L'])
                fileNumber = random.randint(0, len(mpFiles)-1)
                defaultOutput = "hw:Headphones"
                if os.path.exists('/var/snap/mpg123-core/current/output.json'):
                    msg += '/var/snap/mpg123-core/current/output.json present, trying to read\n'
                    data = json.load(open('/var/snap/mpg123-core/current/output.json', 'r'))
                    try:
                        defaultOutput = data['output']
                    except:
                        msg += 'json file malformed, default output will still be %s\n' % defaultOutput
                else:
                    msg += 'no /var/snap/mpg123-core/current/output.json detected, using %s as output\n' % defaultOutput
                myCommand = "mpg123.bin -o alsa:%s %s " % (defaultOutput, mpFiles[fileNumber])
                msg += 'Trying command: %s\n' % myCommand
                process = subprocess.Popen(myCommand.split(), start_new_session=True)
                msg += 'Started music: %s\n' % mpFiles[fileNumber]
            else:
                msg += "Couldn't start music - no mp3 available in /var/snap/mpg123-core/current\n"
        elif command == 'stop':
            if process:
                msg += 'Stopping music\n'
                process.kill()
                msg += 'Done\n'
            else:
                msg += 'No music playing right now, nothing to stop\n'
    else:
        msg += 'Only GET accepted here\n'
    msg += 'Jukebox is done'
    return msg


if __name__=="__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
