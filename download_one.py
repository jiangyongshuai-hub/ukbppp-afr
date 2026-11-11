#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UKB-PPP 非洲人群(AFR) pQTL 单文件下载脚本
================================================
运行环境: GitHub Actions (ubuntu, 海外 IP, 不受 Synapse 地区封禁)

用法:
    python download_one.py [HGNC蛋白符号]

- 带参数: 下载指定蛋白(如 APOE)的 AFR tar 文件
- 不带参数或参数为空: 下载非洲文件夹里第一个蛋白的 tar 文件(试通用)

依赖: pip install synapseclient
环境变量: SYNAPSE_AUTH_TOKEN  (Synapse Personal Access Token, view+download 权限)
"""
import os
import sys

import synapseclient

AFR_FOLDER = "syn51365304"   # UKB-PPP 非洲人群 pGWAS 汇总统计量文件夹
OUT_DIR = "output"


def _id(c):
    return c["id"] if isinstance(c, dict) else c.id


def _name(c):
    return c["name"] if isinstance(c, dict) else c.name


def main():
    token = os.environ.get("SYNAPSE_AUTH_TOKEN")
    if not token:
        print("[错误] 未设置环境变量 SYNAPSE_AUTH_TOKEN", file=sys.stderr)
        sys.exit(2)

    target = sys.argv[1].strip().upper() if len(sys.argv) > 1 else ""

    syn = synapseclient.Synapse()
    syn.login(authToken=token)

    print("列出非洲人群文件夹 %s ..." % AFR_FOLDER)
    children = list(syn.getChildren(AFR_FOLDER, includeTypes=["file"]))
    tars = [c for c in children if _name(c).endswith(".tar")]
    print("共找到 %d 个蛋白 tar 文件" % len(tars))

    if target:
        matches = [c for c in tars if _name(c).upper().startswith(target + "_")]
        if not matches:
            print("[错误] 找不到蛋白 %s 的 tar 文件" % target, file=sys.stderr)
            sys.exit(3)
        chosen = matches[0]
    else:
        chosen = tars[0]

    print("下载: %s  (id=%s)" % (_name(chosen), _id(chosen)))
    os.makedirs(OUT_DIR, exist_ok=True)
    f = syn.get(_id(chosen), downloadLocation=OUT_DIR)
    size_mb = os.path.getsize(f.path) / 1e6
    print("下载完成: %s  (%.1f MB)" % (f.path, size_mb))


if __name__ == "__main__":
    main()
