// Tiny CLI wrapper around FreeSynd's dernc to unpack one RNC-1 file.
// Build: g++ -std=c++17 -I freesynd/utils/include unrnc.cpp \
//          freesynd/utils/src/dernc.cpp -o /tmp/unrnc
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include "fs-utils/io/dernc.h"

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: %s in.dat out.bin\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("open in"); return 1; }
    fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
    std::vector<uint8_t> in(sz);
    if (fread(in.data(), 1, sz, f) != (size_t)sz) { perror("read"); return 1; }
    fclose(f);
    if (!rnc::isRncCompressed(in.data())) {
        fprintf(stderr, "not RNC-compressed; copying through\n");
        FILE *o = fopen(argv[2], "wb"); fwrite(in.data(),1,sz,o); fclose(o); return 0;
    }
    size_t out_len = 0;
    rnc::unpackedLength(in.data(), out_len);
    std::vector<uint8_t> out(out_len);
    size_t real = out_len;
    auto rc = rnc::unpack(in.data(), out.data(), real);
    if (rc != rnc::kOk) { fprintf(stderr, "unpack failed: %s\n", rnc::errorString(rc)); return 1; }
    FILE *o = fopen(argv[2], "wb"); fwrite(out.data(),1,real,o); fclose(o);
    fprintf(stderr, "ok: %ld -> %zu bytes\n", sz, real);
    return 0;
}
