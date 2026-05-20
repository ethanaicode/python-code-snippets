import re

# 仅针对解码后的 MySQL binlog 文件进行处理，可以把其中的 DELETE 语句还原成 INSERT 语句，方便恢复数据
# 推荐对 binlog 文件分割后进行处理，避免内存占用过大

INPUT_FILE = "data/attack.sql"
OUTPUT_FILE = "data/recover.sql"

TABLE_COLUMNS = {
    "cn_group_chats": [
        "id",
        "sender_id",
        "group_id",
        "room_id",
        "type",
        "message",
        "status",
        "reactions",
        "time",
        "updated_at"
    ],

    "cn_chat_rooms": [
        "id",
        "name",
        "description",
        "cover_image",
        "room_notice_message",
        "room_notice_class",
        "is_protected",
        "password",
        "is_visible",
        "chat_validity",
        "slug",
        "allowed_users",
        "allow_guest_view",
        "ad_chat_right_bar",
        "ad_chat_left_bar",
        "show_background",
        "background_image",
        "status",
        "created_by",
        "hide_chat_list",
        "disable_private_chats",
        "disable_group_chats",
        "user_list_type",
        "user_list_auth_roles",
        "room_auto_join"
    ]
}


def clean_value(value):
    value = value.strip()

    # NULL
    if value == "NULL":
        return "NULL"

    return value


def build_insert(table_name, values):
    if table_name not in TABLE_COLUMNS:
        print(f"[跳过未知表] {table_name}")
        return None

    columns = TABLE_COLUMNS[table_name]

    if len(columns) != len(values):
        print(
            f"[字段数量不匹配] {table_name} "
            f"columns={len(columns)} values={len(values)}"
        )
        return None

    col_sql = ", ".join(f"`{c}`" for c in columns)
    val_sql = ", ".join(values)

    return (
        f"INSERT INTO `{table_name}` "
        f"({col_sql}) VALUES ({val_sql});"
    )


def main():

    current_table = None
    current_values = []

    inserts = []

    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for line in lines:

        # 匹配 DELETE FROM
        table_match = re.search(
            r"### DELETE FROM `[^`]+`\.`([^`]+)`",
            line
        )

        if table_match:

            # 保存上一条
            if current_table and current_values:
                sql = build_insert(current_table, current_values)
                if sql:
                    inserts.append(sql)

            current_table = table_match.group(1)
            current_values = []

            continue

        # 匹配字段值
        value_match = re.search(
            r"###\s+@\d+=(.*?)(?: /\*|$)",
            line
        )

        if value_match:
            value = clean_value(value_match.group(1))
            current_values.append(value)

            continue

        # COMMIT 时结束
        if "COMMIT" in line:

            if current_table and current_values:
                sql = build_insert(current_table, current_values)

                if sql:
                    inserts.append(sql)

            current_table = None
            current_values = []

    # 最后一条
    if current_table and current_values:
        sql = build_insert(current_table, current_values)

        if sql:
            inserts.append(sql)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(inserts))

    print(f"生成完成: {OUTPUT_FILE}")
    print(f"INSERT 数量: {len(inserts)}")


if __name__ == "__main__":
    main()