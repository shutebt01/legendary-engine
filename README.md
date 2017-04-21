legendary-engine
=======

UDP based chat program, built to be a single python file

Uses only standard library

## Packet structure

Uses a pseudopacket of an array that is JSON encoded;

|type|src-name|src-group|data|
|----|--------|---------|----|
|Either Message or Event|Soruce Uname|Source Room|Packet type data|
