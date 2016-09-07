#!/bin/bash
trap 'kill %1' SIGINT
python azimuth_controller_server.py & python elevation_controller_server.py
trap - SIGINT
