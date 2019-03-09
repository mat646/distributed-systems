//
// Created by Mateusz Sokol on 06.03.19.
//

#include "contract.h"
#include <stdlib.h>
#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>

token init_token() {
    message m;

    m.msg[1] = 'a';

    access_record ac;

    ac.idx = 0;

    token t;

    t.msg = m;
    t.ac_rec = ac;

    t.type = CONNECT;

    return t;
}

struct sockaddr_in init_tcp_socket_server(int *socket_fd, int port) {

    *socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (*socket_fd == -1) {
        printf("ERROR: can't create socket\n");
        exit(1);
    }

    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t) port);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if ((bind(*socket_fd, (struct sockaddr *) &addr, sizeof(addr))) != 0) {
        printf("ERROR: socket bind failed\n");
        exit(1);
    }

    if ((listen(*socket_fd, 10)) != 0) {
        printf("ERROR: listen failed\n");
        exit(1);
    }

    return addr;
}

void init_tcp_socket_client(int *socket_ds, int port, struct sockaddr_in *addr) {

    *socket_ds = socket(AF_INET, SOCK_STREAM, 0);
    if (*socket_ds == -1) {
        printf("inet: can't create socket\n");
        exit(1);
    }

    //struct sockaddr_in addr;
    addr->sin_family = AF_INET;
    addr->sin_port = htons((uint16_t) port);
    addr->sin_addr.s_addr = htonl(INADDR_ANY);

}

void root_proc() {

    //init_tcp_socket_server(&socket_in, port, address);


}

void candidate_prc() {

}

int main(int argc, char **argv) {

    char name[100];
    int protocol;
    char address[100];
    int port;
    char neigh_address[100];
    int neigh_port;
    int token_flag;
    int socket_in;
    int socket_out;
    int access_idx;
    struct sockaddr_in neighbour;

    if (argc == 1 || argv[1] == NULL || argv[2] == NULL || argv[3] == NULL || argv[4] == NULL || argv[5] == NULL) {
        printf("Execute args:\n 1. clientID\n 2. port\n 3. neighbour address\n 4. neighbour port\n"
               " 6. have token\n 6. protocol tcp/udp\n");
        exit(1);
    }

    sscanf(argv[1], "%s", name);
    sscanf(argv[2], "%d", &port);
    sscanf(argv[3], "%s", neigh_address);
    sscanf(argv[4], "%d", &neigh_port);
    sscanf(argv[5], "%d", &token_flag);
    sscanf(argv[6], "%d", &protocol);

    // opening socket

    if (token_flag == 1) {

        struct sockaddr_in my_addr = init_tcp_socket_server(&socket_in, port);

        struct sockaddr_in client;
        socklen_t len = sizeof(client);
        int socket_cli = accept(socket_in, (struct sockaddr *) &client, &len);
        if (socket_cli < 0) {
            printf("server acccept failed...\n");
            exit(1);
        }

        token read_token;

        read(socket_cli, &read_token, sizeof(token));

        printf("%d\n", read_token.port);

        neigh_port = read_token.port;

        write(socket_cli, &port, sizeof(port));

        sleep(2);

        //neighbour = client;

        printf("tyle\n");

    } else {

        struct sockaddr_in addr;

        init_tcp_socket_client(&socket_out, neigh_port, &addr);

        while (connect(socket_out, (const struct sockaddr *) &addr, sizeof(addr)) == -1) {
            printf("inet: can't connect\n");
        }

        token token1;

        token1.type = CONNECT;
        token1.port = port;

        printf("READING!\n");

        if (write(socket_out, &token1, sizeof(token)) < 0) {
            printf("can't log on server\n");
        }

        int porrrt;

        read(socket_out, &porrrt, sizeof(porrrt));


        printf("%d\n", porrrt);

        neigh_port = porrrt;

        //init_tcp_socket_client(&socket_out, log_response1.port, log_response1.address);


        init_tcp_socket_server(&socket_in, port);

        printf("SERVER established\n");
    }

    // network loop

    while (1) {

        if (token_flag == 0) {


            printf("0 %d\n", port);

            struct token tk;

            //init_tcp_socket_server(&socket_in, port);

            struct sockaddr_in client;
            socklen_t len = sizeof(client);
            int cli = accept(socket_in, (struct sockaddr *) &client, &len);
            if (cli < 0) {
                printf("server acccept failed...\n");
                exit(1);
            } else {
                printf("success\n");
            }


            read(cli, &tk, sizeof(tk));


            // obsluga podlaczania nowych osob
            if (tk.type == CONNECT) {

                write(cli, &neigh_port, sizeof(neigh_port));

                neigh_port = tk.port;

                sleep(2);

                continue;

            }

            token_flag = 1;
            printf("MINE TIME!\n");

            sleep(1);

        } else {

            printf("1 %d\n", port);

            token tk;
            tk.type = TOKEN;

            printf("trying to connect to %d\n", neigh_port);

//            struct sockaddr_in addr;
//            addr.sin_family = AF_INET;
//            addr.sin_port = htons((uint16_t) neigh_port);
//            addr.sin_addr.s_addr = htonl(INADDR_ANY);

            struct sockaddr_in addr;

            init_tcp_socket_client(&socket_out, neigh_port, &addr);

            while (connect(socket_out, (const struct sockaddr *) &addr, sizeof(addr)) == -1) {
                //printf("inet: can't connect\n");
            }

            write(socket_out, &tk, sizeof(tk));

            token_flag = 0;

            printf("TOKEN PASSED!\n");

        }

        sleep(1);

    }

}


