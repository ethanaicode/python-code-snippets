"""通过 scp 下载服务器当天的数据库备份到本地。

用法: python db_backup_download.py <ssh主机,如 user@host 或 ~/.ssh/config 中的别名> [-p 端口] [-d 日期YYYYMMDD] [-t 文件名模板]
例: -t flarum_upflow_{day}.sql.gz
依赖 SSH 密钥免密登录;否则 scp 会在终端提示输入密码。
"""
import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

REMOTE_DIR = "/www/backup/db"
LOCAL_DIR = Path("/Volumes/MAC_SN7100_01/WebBackup/sql")
FILE_TEMPLATE = "think_desktop_client_{day}.sql.gz"


def main(host, day, port, template):
    if not LOCAL_DIR.is_dir():
        sys.exit(f"本地目录不存在(磁盘未挂载?): {LOCAL_DIR}")

    name = template.format(day=day)
    target = LOCAL_DIR / name
    # 先下载到临时文件,成功后再改名,避免留下不完整的备份
    tmp = target.with_suffix(target.suffix + ".part")

    cmd = ["scp"]
    if port:
        cmd += ["-P", str(port)]
    result = subprocess.run(cmd + [f"{host}:{REMOTE_DIR}/{name}", str(tmp)])
    if result.returncode != 0:
        tmp.unlink(missing_ok=True)
        sys.exit(f"下载失败, scp 退出码 {result.returncode}")

    tmp.replace(target)
    print(f"已保存: {target} ({target.stat().st_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("host", help="user@host 或 ssh 配置别名")
    ap.add_argument("-p", "--port", type=int, help="SSH 端口,不填则使用 ssh 配置或 22")
    ap.add_argument("-d", "--day", default=date.today().strftime("%Y%m%d"), help="备份日期 YYYYMMDD,默认今天")
    ap.add_argument("-t", "--template", default=FILE_TEMPLATE, help="文件名模板,{day} 会替换为日期")
    args = ap.parse_args()
    main(args.host, args.day, args.port, args.template)
