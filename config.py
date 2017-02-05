import os


def build_lighttpd_config(WEB_SRV_HOST, WEB_SRV_PORT, WEB_CLIENT_PORT):
    """Creates lighttpd configuration file"""
    configText = """
var.log_root    = server_root
var.state_dir   = server_root
var.home_dir    = server_root
var.conf_dir    = server_root
server.pid-file = state_dir + "/lighttpd.pid"
server.errorlog = log_root + "/lighttpd.log"
server.document-root = server_root

mimetype.assign = (
    ".html" => "text/html",
    ".txt" => "text/plain",
    ".jpg" => "image/jpeg",
    ".png" => "image/png",
    ".css" => "text/css",
    ".svg" => "image/svg+xml",
    ".js" => "text/javascript"
)

static-file.exclude-extensions = (".py")
server.modules += ( "mod_proxy" )
server.modules += ( "mod_alias" )


"""
    server_root_path = os.path.dirname(os.path.abspath(__file__))
    file = open(server_root_path + '/lighttpd.develop', 'w')
    file.write('var.server_root = "' + str(server_root_path) + '"\n')
    file.write('server.port = ' + WEB_CLIENT_PORT + '\n')

    file.write(configText)
    file.write('alias.url = (\n')
    file.write('"/static/" => "{}",'.format(str(server_root_path) + '/static/'))
    file.write('\n)\n')
    file.write('\n$HTTP["url"] !~ "^/static" {\n')
    file.write('proxy.balance = "hash" \n')
    file.write('proxy.server = ( "" =>\n')
    file.write('( (\n')
    file.write(' "host" => "{}",\n "port" => {}\n'.format(WEB_SRV_HOST, WEB_SRV_PORT))
    file.write('))\n')
    file.write(')\n')
    file.write('}\n')
    file.close()
    return
