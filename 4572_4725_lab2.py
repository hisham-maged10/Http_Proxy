import sys
import os
import enum
import socket
from _thread import *

#done
class HttpRequestInfo(object):
    """
    Represents a HTTP request information

    Since you'll need to standardize all requests you get
    as specified by the document, after you parse the
    request from the TCP packet put the information you
    get in this object.

    To send the request to the remote server, call to_http_string
    on this object, convert that string to bytes then send it in
    the socket.

    client_address_info: address of the client;
    the client of the proxy, which sent the HTTP request.

    requested_host: the requested website, the remote website
    we want to visit.

    requested_port: port of the webserver we want to visit.

    requested_path: path of the requested resource, without
    including the website name.

    NOTE: you need to implement to_http_string() for this class.
    """

    def __init__(self, client_info, method: str, requested_host: str,
                 requested_port: int,
                 requested_path: str,
                 headers: list):
        self.method = method
        self.client_address_info = client_info
        self.requested_host = requested_host
        self.requested_port = requested_port
        self.requested_path = requested_path
        # Headers will be represented as a list of lists
        # for example ["Host", "www.google.com"]
        # if you get a header as:
        # "Host: www.google.com:80"
        # convert it to ["Host", "www.google.com"] note that the
        # port is removed (because it goes into the request_port variable)
        self.headers = headers

    def to_http_string(self):
        """
        Convert the HTTP request/response
        to a valid HTTP string.
        As the protocol specifies:

        [request_line]\r\n
        [header]\r\n
        [headers..]\r\n
        \r\n

        (just join the already existing fields by \r\n)

        You still need to convert this string
        to byte array before sending it to the socket,
        keeping it as a string in this stage is to ease
        debugging and testing.
        """

        http_string = self.method + " " + self.requested_path + " HTTP/1.0\r\n"
        for i in range(len(self.headers)):
            http_string += self.headers[i][0] +": " + self.headers[i][1] +"\r\n"
        http_string += "\r\n"

        return http_string

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(f"Client:", self.client_address_info)
        print(f"Method:", self.method)
        print(f"Host:", self.requested_host)
        print(f"Port:", self.requested_port)
        stringified = [": ".join([k, v]) for (k, v) in self.headers]
        print("Headers:\n", "\n".join(stringified))

#done
class HttpErrorResponse(object):
    """
    Represents a proxy-error-response.
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def to_http_string(self):
        """ Same as above """
        http_string = str(self.code) + " " + self.message + "\r\n"
        return http_string

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(self.to_http_string())

#done
class HttpRequestState(enum.Enum):
    """
    The values here have nothing to do with
    response values i.e. 400, 502, ..etc.

    Leave this as is, feel free to add yours.
    """
    INVALID_INPUT = 0
    NOT_SUPPORTED = 1
    GOOD = 2
    PLACEHOLDER = -1

#done
def entry_point(proxy_port_number):
    """
    Entry point, start your code here.

    Please don't delete this function,
    but feel free to modify the code
    inside it.
    """
    setup_sockets(proxy_port_number)

    pass

#done
def setup_server_socket(http_request_obj : HttpRequestInfo, client_socket : socket = None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    required_host = http_request_obj.requested_host
    required_port = http_request_obj.requested_port
    http_string = http_request_obj.to_http_string()
    request_byte_arr = http_request_obj.to_byte_array(http_string)
    response = do_server_socket_logic(server_socket,required_host,required_port,request_byte_arr,client_socket)
    
    return response

#done
def do_server_socket_logic(server_socket : socket, required_host: str ,required_port : int, request_byte_arr, client_socket : socket):
    print(f"required_host: {required_host}")
    print(f"required_port: {required_port}")
    server_socket.connect((required_host,int(required_port)))
    server_socket.send(request_byte_arr)
    response = bytearray()
    while True:
        http_response = server_socket.recv(4096)
        response += http_response
        if(len(http_response) == 0):
            break
    
    server_socket.close()

    return response

#done
def setup_sockets(proxy_port_number):
    """
    Socket logic MUST NOT be written in the any
    class. Classes know nothing about the sockets.

    But feel free to add your own classes/functions.

    Feel free to delete this function.
    """
    print("Starting HTTP proxy on port:", proxy_port_number)
    
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    do_socket_logic(proxy_socket,proxy_port_number)
   
    pass

#do socket logic of Proxy, client TCP Connection, basically get the HTTP request and call Http_request_pipeline here and stay on the loop
def do_socket_logic(proxy_socket: socket,proxy_port_number):
    """
    Example function for some helper logic, in case you
    want to be tidy and avoid stuffing the main function.

    Feel free to delete this function.
    """

    proxy_socket.bind(("127.0.0.1",int(proxy_port_number)))
    proxy_socket.listen(10)
    cache = {}
    while True:
        client_socket, address =  proxy_socket.accept()
        print(f"Started conn with {address}")
        start_new_thread(handle_client,(client_socket,cache, address))
    proxy_socket.close()

    pass

# add your logic here, this is called during threading
def handle_client(client_socket,cache, address):
    #get source_addr, http raw data from telnet's input
    telnet_input = bytearray()
    while True:
        data = client_socket.recv(4096)
        if(data.decode("utf-8") == '\r\n'):
            break
        telnet_input += data
    print(telnet_input)
    #do the request pipeine then check for error 
    http = http_request_pipeline(address, telnet_input.decode('utf-8'))
    check = isinstance(http,HttpErrorResponse)
    if check :
        error_string = http.to_http_string()
        client_socket.send(http.to_byte_array(error_string))
        client_socket.close()
        pass
    #remove next line when you implement your part and uncomment the previous lines
    # http = HttpRequestInfo(("127.0.0.1", 18888), "GET", "www.apache.org", 80, "/", [["Host", "www.google.com"], ["Accept", "application/json"]])
    response = cache[http.requested_host+":"+str(http.requested_port)+http.requested_path] if http.requested_host+":"+str(http.requested_port)+http.requested_path in cache else setup_server_socket(http,client_socket)
    cache[http.requested_host+":"+str(http.requested_port)+http.requested_path] = response
    client_socket.send(response)
    client_socket.close()
    print(f"Finished!")
    pass
#Http's Highlevel method, everything concerning Validation, parsing, sanitizing is put here, returns HTTPRequestInfo in the end to be used to send TCP to needed website
#Returns HTTPErrorResponse object if not valid using validity local variable
def http_request_pipeline(source_addr, http_raw_data):
    """
#Returns HTTPErrorResponse object if not valid using validity local variable

    - Validates the given HTTP request and returns
      an error if an invalid request was given.
    - Parses it
    - Returns a sanitized HttpRequestInfo

    returns:
     HttpRequestInfo if the request was parsed correctly.
     HttpErrorResponse if the request was invalid.

    Please don't remove this function, but feel
    free to change its content
    """
    # Parse HTTP request
    print(f"Http raw data: {http_raw_data}")
    print(f"source address(tuble): {source_addr}")
    validity = check_http_request_validity(http_raw_data)
    if(validity == HttpRequestState.NOT_SUPPORTED):
        code = 500
        message = "Not supported"
        return HttpErrorResponse(code,message)
    elif(validity == HttpRequestState.INVALID_INPUT):
        code = 400
        message = "Bad Request"
        return HttpErrorResponse(code, message)
    # Return error if needed, then:
    httprequest =  parse_http_request(source_addr, http_raw_data)
    # sanitize_http_request()
    # Validate, sanitize, return Http object.
   
    return httprequest

#parses the contents of an http request, and returns an HTTP Request Object
def parse_http_request(source_addr, http_raw_data):
    """
    This function parses a "valid" HTTP request into an HttpRequestInfo
    object.
    """
    
    # Replace this line with the correct values.
    listoflists = tokenization(http_raw_data)
    method = listoflists[0]
    method = method.upper()
    url = listoflists[1]
    url = url.lower()
    httpversion = listoflists[2]
    host = ""
    path = ""
    if(url.startswith('/')):
        path = url
        hostarray = listoflists[3]
        host_and_port = hostarray[0][1]
        host_and_port_array = host_and_port.split(':')
        if(len(host_and_port_array) < 2):
            host = host_and_port_array[0]
            port = 80
        else:
            host = host_and_port_array[0]
            port = host_and_port_array[1]
    else:
        hostarray =  url.split('://')
        host_and_port = hostarray[1]
        host_and_port_array = host_and_port.split(':')
        if(len(host_and_port_array) < 2):
            port = 80
            host_and_path = host_and_port_array[0]
        else:
            port_path = host_and_port_array[1]
            if(port_path.endswith('/')):
                port = port_path.split('/')[0]
                path = '/' + port_path.split('/')[1]
            host_and_path = host_and_port_array[0]
        host_and_path_array = host_and_path.split('/', 1)
        host = host_and_path_array[0]
        #port = '/' + host_and_path_array[1]
        if(path != ""):
            if(len(host_and_path_array) == 2):
                path = "/" + host_and_path_array[1]
            else:
                path = "/"
    header = listoflists[3]            
    ret = HttpRequestInfo(source_addr, method, host, port, path, header)
    return ret

#Checks the http request if it is a valid request
def check_http_request_validity(http_raw_data) -> HttpRequestState:
    """
    Checks if an HTTP request is valid

    returns:
    One of values in HttpRequestState
    """
    print("*" * 50)
    print("[check_http_request_validity] Implement me!")
    print("*" * 50)
    listoflists = tokenization(http_raw_data)
    if(isinstance(listoflists,HttpRequestState)):#to check if the first element is only = 3
        print("NOT IMPLEMENTED")
        return HttpRequestState.INVALID_INPUT
    try:
        method = listoflists[0]
        method = method.upper()
        url = listoflists[1]
        httpversion = listoflists[2]
        print(f"METHOD: {method}  URL: {url}  HTTPVERSION: {httpversion}")
        if(len(method) == 0):
            print("NOT IMPLEMENTED 1")
            return HttpRequestState.INVALID_INPUT
        list_methods = {"GET", "HEAD", "POST", "PUT"}
        if(method not in list_methods):
            print("NOT IMPLEMENTED 2")
            return HttpRequestState.INVALID_INPUT
        if(len(url) == 0):
            print("NOT IMPLEMENTED 3")
            return HttpRequestState.INVALID_INPUT
        if(url == '/'):
            hostlist = listoflists[3]
            print(f"VALUEEEEEEEEE: {hostlist[0]}")
            if(len(hostlist[0][1]) == 0):
                print("NOT IMPLEMENTED RELATIVE PATH")
                return HttpRequestState.INVALID_INPUT
        if(len(httpversion) == 0):
            print("NOT IMPLEMENTED 4")
            return HttpRequestState.INVALID_INPUT
        if( (httpversion.split("/")[1] != '1.1') and (httpversion.split("/")[1] != '1.0')):
            print(F"HTTP VERSIONNNNNNNNNNNNNN: {httpversion}")
            print(httpversion.split("/")[1])
            print("NOT IMPLEMENTED Http version")
            return HttpRequestState.INVALID_INPUT
        if(not httpversion.startswith("HTTP/")):
            print("NOT IMPLEMENTED 5")
            return HttpRequestState.INVALID_INPUT
        if(method != "GET"):
            print("NOT SUPPORTED")
            return HttpRequestState.NOT_SUPPORTED
        return HttpRequestState.GOOD
    except Exception as e: 
        print(e)
        print("Error in catch")
        return HttpRequestState.INVALID_INPUT
    # return HttpRequestState.GOOD (for example)
    # return HttpRequestState.PLACEHOLDER

def tokenization(http_raw_data):
    print("http raw data {http_raw_data}")
    listoflists = []
    http_raw_data = http_raw_data.rstrip()
    line_elements = http_raw_data.split("\r\n")
    line_elements[0] = line_elements[0].rstrip()
    print(f"Line_elements: {line_elements}")
    first_line = line_elements[0].split(" ")
    if(len(first_line) != 3):
        print("NOT IMPLEMENTED")
        return HttpRequestState.INVALID_INPUT
    for elem in first_line:
        listoflists.append(elem)
    listofheaders = []
    for i in range (1, len(line_elements) ):
        line_elements[i] = line_elements[i].rstrip()
        if(":" not in line_elements[i]):
            print("NOT IMPLEMENTED")
            return HttpRequestState.INVALID_INPUT
        header_line = line_elements[i].split(":", 1)
        print(f"HEADEER LINE AFTER SPLIT: {header_line}")
        if(len(header_line) == 2):
            listofheaders.append([header_line[0].strip(), header_line[1].strip()])
        else:
            print("NOT IMPLEMENTED")
            return HttpRequestState.INVALID_INPUT
    listoflists.append(listofheaders)
    print(f"List of Lists: {listoflists}")
    return listoflists

#Sanitizing, making the HTTP request of the correct format, before sending to server
def sanitize_http_request(request_info: HttpRequestInfo):
    """
    Puts an HTTP request on the sanitized (standard) form
    by modifying the input request_info object.

    for example, expand a full URL to relative path + Host header.

    returns:
    nothing, but modifies the input object
    """
  


#######################################
# Leave the code below as is.
#######################################

#Helper method
def get_arg(param_index, default=None):
    """
        Gets a command line argument by index (note: index starts from 1)
        If the argument is not supplies, it tries to use a default value.

        If a default value isn't supplied, an error message is printed
        and terminates the program.
    """
    try:
        return sys.argv[param_index]
    except IndexError as e:
        if default:
            return default
        else:
            print(e)
            print(
                f"[FATAL] The comand-line argument #[{param_index}] is missing")
            exit(-1)    # Program execution failed.

#Checks file name for testing compatability
def check_file_name():
    """
    Checks if this file has a valid name for *submission*

    leave this function and as and don't use it. it's just
    to notify you if you're submitting a file with a correct
    name.
    """
    script_name = os.path.basename(__file__)
    import re
    matches = re.findall(r"(\d{4}_){,2}lab2\.py", script_name)
    if not matches:
        print(f"[WARN] File name is invalid [{script_name}]")
    else:
        print(f"[LOG] File name is correct.")

# Not to be changed, Entry point of Program
def main():
    """
    Please leave the code in this function as is.

    To add code that uses sockets, feel free to add functions
    above main and outside the classes.
    """
    print("\n\n")
    print("*" * 50)
    print(f"[LOG] Printing command line arguments [{', '.join(sys.argv)}]")
    check_file_name()
    print("*" * 50)

    # This argument is optional, defaults to 18888
    proxy_port_number = get_arg(1, 18888)
    entry_point(proxy_port_number)


if __name__ == "__main__":
    main()