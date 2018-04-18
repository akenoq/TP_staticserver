import os
import socket

import debugger

import service


def child_proc(
        sock, rdir):
    print("worker PID={}".format(os.getpid()))
    buf_size = 1024
    while 1:
        # (сокет, адрес клиента)
        (cl_conn, cl_addr) = sock.accept()
        debugger.log(str((cl_conn, cl_addr)))
        data = cl_conn.recv(buf_size)
        # если за таймаут не получены байты
        # или кл. откл. - recv вернет пустой обьект
        if len(data.strip()) == 0:
            # print("No data")
            cl_conn.close()
            continue

        resp = service.process(rdir, data)
        # print("eee")
        cl_conn.sendall(resp)
        cl_conn.close()


def run(cpu_num, rdir, listeners, port):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0.', port))
    sock.listen(listeners)

    print("Server started on port {}".format(port))
    print("PID={}".format(os.getpid()))

    workers = []
    for i in range(cpu_num):
        new_pid = os.fork()
        if new_pid == 0:
            child_proc(sock, rdir)
            break
        else:
            workers.append(new_pid)

    sock.close()

    for child_pid in workers:
        os.waitpid(child_pid, 0)
