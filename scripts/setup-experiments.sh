#!/bin/bash

chmod +x ./init-controller.sh
chmod +x ./run-mininet.sh

# # Inicia Floodlight
./init-controller.sh

# Inicia arquivo com topologia
./run-mininet.sh
