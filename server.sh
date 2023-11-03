#!/bin/bash
pid=$(lsof -ti :5000)
if [ -z "$pid" ]
then
  echo ""
else
  kill -9 $pid
  echo "Processo $pid foi finalizado"
fi
python3.11 server.py

