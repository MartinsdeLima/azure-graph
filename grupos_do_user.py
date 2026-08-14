#!/usr/bin/env python3
import os
import sys
import requests

GRAPH_API = "https://graph.microsoft.com/v1.0"

GRAPH_TOKEN = os.environ.get("GRAPH_TOKEN")
if not GRAPH_TOKEN:
    raise Exception("⚠️ Variável de ambiente GRAPH_TOKEN não encontrada. Rode:\n"
                    "   export GRAPH_TOKEN=$(az account get-access-token "
                    "--resource-type ms-graph --query accessToken -o tsv)")

headers = {"Authorization": f"Bearer {GRAPH_TOKEN}"}


def get_user_groups(upn: str) -> list[dict]:
    url = f"{GRAPH_API}/users/{upn}/transitiveMemberOf?$select=displayName,id,groupTypes"
    groups = []
    while url:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        for obj in data.get("value", []):
            if obj.get("@odata.type") == "#microsoft.graph.group":
                groups.append({"id": obj["id"], "displayName": obj["displayName"]})
        url = data.get("@odata.nextLink")
    return sorted(groups, key=lambda g: g["displayName"].lower())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python grupos_do_user.py <userPrincipalName>")
        print("Ex:  python grupos_do_user.py joao.silva@empresa.com")
        sys.exit(1)

    upn = sys.argv[1].strip()
    print(f"\nBuscando grupos de: {upn}\n")

    try:
        groups = get_user_groups(upn)
    except requests.HTTPError as e:
        print(f"❌ Erro na API: {e}")
        sys.exit(1)

    if not groups:
        print("Nenhum grupo encontrado.")
    else:
        print(f"Total: {len(groups)} grupo(s)\n")
        for g in groups:
            print(f"  {g['displayName']}")
