import pyodbc

print(" DB MODULE LOADED")

# ---------------------------------------------------
# 🔌 DB CONNECTION
# ---------------------------------------------------
try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=13.127.102.100;"
        "DATABASE=acp_swms;"
        "UID=sa;"
        "PWD=Mobillor@2021"
    )
    print(" DB Connected Successfully")
except Exception as e:
    print("DB CONNECTION ERROR:", str(e))


# ---------------------------------------------------
#  UPSERT FUNCTION
# ---------------------------------------------------
def upsert_token_usage(userId, sessionId, total, prompt, completion):
    print(" DB FUNCTION CALLED")

    query = """
    MERGE token_usage AS target
    USING (SELECT ? AS user_id, ? AS session_id) AS source
    ON target.user_id = source.user_id AND target.session_id = source.session_id

    WHEN MATCHED THEN
        UPDATE SET
            total_tokens = target.total_tokens + ?,
            prompt_tokens = target.prompt_tokens + ?,
            completion_tokens = target.completion_tokens + ?,
            total_calls = target.total_calls + 1,
            updated_at = GETDATE()

    WHEN NOT MATCHED THEN
        INSERT (user_id, session_id, total_tokens, prompt_tokens, completion_tokens, total_calls)
        VALUES (?, ?, ?, ?, ?, 1);
    """

    try:
        cursor = conn.cursor()   

        cursor.execute(
            query,
            userId, sessionId,
            total, prompt, completion,
            userId, sessionId, total, prompt, completion
        )

        conn.commit()

        print("DB write success:", userId, sessionId)

    except Exception as e:
        print(" DB ERROR:", str(e))