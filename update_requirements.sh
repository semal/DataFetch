#!/usr/bin/env bash

venv/bin/pip list >requirements.txt
sed -i "s/ (/==/g" requirements.txt
sed -i "s/)//g" requirements.txt
sed -i "/pip/d" requirements.txt
sed -i "/setuptools/d" requirements.txt
sed -i "/wheel/d" requirements.txt