from __future__ import annotations
import argparse, sys
from pathlib import Path
from .config import load_config
from .errors import ScaffoldError
from .generator import render_repository
from .git import initialize_repository
from .stages import create_repository,inspect_config,plan_config
from .verification import verify_generated_repository

def parser():
    p=argparse.ArgumentParser(description="中央领域仓通用脚手架"); sub=p.add_subparsers(dest="command",required=True)
    for name in ("inspect","validate"):
        q=sub.add_parser(name); q.add_argument("--config",type=Path,required=True)
    q=sub.add_parser("plan"); q.add_argument("--config",type=Path,required=True); q.add_argument("--output",type=Path,required=True)
    q=sub.add_parser("render"); q.add_argument("--config",type=Path,required=True); q.add_argument("--output",type=Path,required=True)
    q=sub.add_parser("git-init"); q.add_argument("--output",type=Path,required=True)
    q=sub.add_parser("verify"); q.add_argument("--output",type=Path,required=True); q.add_argument("--require-git",action="store_true")
    q=sub.add_parser("create"); q.add_argument("--config",type=Path,required=True); q.add_argument("--output",type=Path,required=True); q.add_argument("--keep-failed-output",action="store_true")
    return p
def main(argv=None):
    args=parser().parse_args(argv)
    try:
        if args.command=="inspect": print(inspect_config(args.config))
        elif args.command=="validate": load_config(args.config); print("配置校验通过")
        elif args.command=="plan": print(plan_config(args.config,args.output))
        elif args.command=="render": render_repository(load_config(args.config),args.output); print(args.output.resolve())
        elif args.command=="git-init":
            c=load_config(args.output/"domain.yaml")
            verify_generated_repository(args.output,False)
            print(initialize_repository(args.output,c.domain.default_branch))
        elif args.command=="verify": verify_generated_repository(args.output,args.require_git); print("生成仓校验通过")
        elif args.command=="create":
            sha=create_repository(args.config,args.output,args.keep_failed_output); print(f"生成完成：{args.output.resolve()}\ncommit: {sha}")
        return 0
    except ScaffoldError as exc:
        print(f"{args.command} 阶段失败：{exc}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
