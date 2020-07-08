from flask import *
import subprocess
app = Flask(__name__)

@app.route('/')
def index():
    f = open('test_vpn_ip.txt', 'r')
    lines = f.readlines()
    vpn_ip = lines[0]
    kali_ip = lines[1]
    vuln_ip = lines[2]
    return render_template('index_template.html', vpn_ip=vpn_ip, kali_ip=kali_ip, vuln_ip=vuln_ip)

@app.route('/<name>')
def get_vpn(name=None):
    cmd = "pivpn -a -n " + name + " nopass -d 1000"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    app.logger.debug(output)
    app.logger.warning(error)

    ovpn_file = send_from_directory('/home/ubuntu/ovpns/', filename = name + '.ovpn', as_attachment = True)
    return ovpn_file

    
