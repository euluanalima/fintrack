import pandas as pd

TX_COLUMNS = ["id", "description", "amount", "type", "category", "date"]
GOAL_COLUMNS = ["id", "name", "target_amount", "current_amount", "deadline", "created_at"]
HISTORY_COLUMNS = ["id", "amount", "movement_type", "date"]


def _df(data, columns):
    if not data:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(data)
    for col in columns:
        if col not in frame.columns:
            frame[col] = None
    return frame[columns]


def add_transaction(client, user_id, description, amount, transaction_type, category, transaction_date):
    client.table("transactions").insert({
        "user_id": user_id,
        "description": description,
        "amount": float(amount),
        "type": transaction_type,
        "category": category,
        "date": transaction_date,
    }).execute()


def get_transactions(client, user_id):
    response = (
        client.table("transactions")
        .select("id,description,amount,type,category,date")
        .eq("user_id", user_id)
        .order("date", desc=True)
        .order("id", desc=True)
        .execute()
    )
    frame = _df(response.data, TX_COLUMNS)
    if not frame.empty:
        frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce").fillna(0.0)
    return frame


def delete_transaction(client, user_id, transaction_id):
    (
        client.table("transactions")
        .delete()
        .eq("id", int(transaction_id))
        .eq("user_id", user_id)
        .execute()
    )


def create_savings_goal(client, user_id, name, target_amount, deadline=None):
    client.table("savings_goals").insert({
        "user_id": user_id,
        "name": name,
        "target_amount": float(target_amount),
        "deadline": deadline,
    }).execute()


def get_savings_goals(client, user_id):
    goals_response = (
        client.table("savings_goals")
        .select("id,name,target_amount,deadline,created_at")
        .eq("user_id", user_id)
        .order("id", desc=True)
        .execute()
    )
    goals = pd.DataFrame(goals_response.data or [])
    if goals.empty:
        return pd.DataFrame(columns=GOAL_COLUMNS)

    goals["target_amount"] = pd.to_numeric(goals["target_amount"], errors="coerce").fillna(0.0)

    movement_response = (
        client.table("savings_transactions")
        .select("goal_id,amount,movement_type")
        .eq("user_id", user_id)
        .execute()
    )
    movements = pd.DataFrame(movement_response.data or [])

    if movements.empty:
        goals["current_amount"] = 0.0
    else:
        movements["amount"] = pd.to_numeric(movements["amount"], errors="coerce").fillna(0.0)
        movements["signed_amount"] = movements.apply(
            lambda row: row["amount"] if row["movement_type"] == "Depósito" else -row["amount"],
            axis=1,
        )
        totals = movements.groupby("goal_id", as_index=False)["signed_amount"].sum()
        goals = goals.merge(totals, how="left", left_on="id", right_on="goal_id")
        goals["current_amount"] = goals["signed_amount"].fillna(0.0)
        goals = goals.drop(columns=[c for c in ["goal_id", "signed_amount"] if c in goals.columns])

    for col in GOAL_COLUMNS:
        if col not in goals.columns:
            goals[col] = None
    return goals[GOAL_COLUMNS]


def _current_goal_amount(client, user_id, goal_id):
    response = (
        client.table("savings_transactions")
        .select("amount,movement_type")
        .eq("user_id", user_id)
        .eq("goal_id", int(goal_id))
        .execute()
    )
    total = 0.0
    for item in response.data or []:
        value = float(item["amount"])
        total += value if item["movement_type"] == "Depósito" else -value
    return total


def add_savings_movement(client, user_id, goal_id, amount, movement_type, movement_date):
    goal_response = (
        client.table("savings_goals")
        .select("id")
        .eq("id", int(goal_id))
        .eq("user_id", user_id)
        .execute()
    )
    if not goal_response.data:
        raise ValueError("Meta não encontrada.")

    amount = float(amount)
    current_amount = _current_goal_amount(client, user_id, goal_id)
    if movement_type == "Retirada" and amount > current_amount:
        raise ValueError("A retirada não pode ser maior que o valor guardado.")

    client.table("savings_transactions").insert({
        "user_id": user_id,
        "goal_id": int(goal_id),
        "amount": amount,
        "movement_type": movement_type,
        "date": movement_date,
    }).execute()


def get_savings_history(client, user_id, goal_id):
    response = (
        client.table("savings_transactions")
        .select("id,amount,movement_type,date")
        .eq("user_id", user_id)
        .eq("goal_id", int(goal_id))
        .order("date", desc=True)
        .order("id", desc=True)
        .execute()
    )
    frame = _df(response.data, HISTORY_COLUMNS)
    if not frame.empty:
        frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce").fillna(0.0)
    return frame


def delete_savings_goal(client, user_id, goal_id):
    (
        client.table("savings_goals")
        .delete()
        .eq("id", int(goal_id))
        .eq("user_id", user_id)
        .execute()
    )
