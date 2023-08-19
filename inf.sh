#!/bin/bash
echo "inference begins!"
CUDA_VISIBLE_DEVICES=0 python3 convert.py --hpfile configs/freevc.json --ptfile f0/ckpt.pth --txtpath convert.txt --outdir outputs/freevc

