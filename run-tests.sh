#!/usr/bin/bash

# for i in $(seq -w 1 10); do
#     echo "Test $i"
#     cp testcase/T$i/input.txt .
#     python compiler.py
#     diff testcase/T$i/tokens.txt tokens.txt
#     diff testcase/T$i/lexical_errors.txt lexical_errors.txt
# done

cp testcase/T10/input.txt .
python compiler.py
# diff testcase/T05/tokens.txt tokens.txt
# diff testcase/T05/lexical_errors.txt lexical_errors.txt
