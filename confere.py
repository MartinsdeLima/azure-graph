#!/usr/bin/env python3
import os
import requests
import csv

GRAPH_API = "https://graph.microsoft.com/v1.0"

# Lê o token que exportamos via Azure CLI
GRAPH_TOKEN = os.environ.get("GRAPH_TOKEN")
if not GRAPH_TOKEN:
    raise Exception("⚠️ Variável de ambiente GRAPH_TOKEN não encontrada. Rode:\n"
                    "   export GRAPH_TOKEN=$(az account get-access-token "
                    "--resource-type ms-graph --query accessToken -o tsv)")

headers = {"Authorization": f"Bearer {GRAPH_TOKEN}"}


def get_group_id(group_name):
    url = f"{GRAPH_API}/groups?$filter=displayName eq '{group_name}'"
    resp = requests.get(url, headers=headers).json()
    if resp.get("value"):
        return resp["value"][0]["id"]
    return None


def get_group_members(group_id):
    # Usa transitiveMembers para incluir nested groups
    url = f"{GRAPH_API}/groups/{group_id}/transitiveMembers?$select=id,userPrincipalName"
    members = []
    while url:
        resp = requests.get(url, headers=headers).json()
        for m in resp.get("value", []):
            if "userPrincipalName" in m:
                members.append(m["userPrincipalName"].lower())
        url = resp.get("@odata.nextLink", None)
    return set(members)


# === Lógica principal ===
with open("grupos.txt") as f:
    bases = [line.strip() for line in f if line.strip()]

with open("faltando.csv", "w", newline="") as faltando_csv, open("completos.csv", "w", newline="") as completos_csv:
    faltando_writer = csv.writer(faltando_csv)
    completos_writer = csv.writer(completos_csv)

    faltando_writer.writerow(["Grupo_MEMBROS", "Usuario_Faltando"])
    completos_writer.writerow(["Grupo_MEMBROS"])

    total = len(bases)
    for idx, base in enumerate(bases, start=1):
        grupos = {
            "ADMINISTRADOR": f"GG_{base}_ADMINISTRADOR",
            "VISUALIZADOR": f"GG_{base}_VISUALIZADOR",
            "DESENVOLVEDOR": f"GG_{base}_DESENVOLVEDOR",
            "MEMBROS": f"GG_{base}_MEMBROS",
        }

        print(f"[{idx}/{total}] Conferindo {grupos['MEMBROS']}...")

        ids = {k: get_group_id(v) for k, v in grupos.items()}
        if not ids["MEMBROS"]:
            print(f" ⚠️ Grupo {grupos['MEMBROS']} não encontrado")
            continue

        membros = get_group_members(ids["MEMBROS"])
        obrigatorios = set()

        for g in ["ADMINISTRADOR", "VISUALIZADOR", "DESENVOLVEDOR"]:
            if ids[g]:
                obrigatorios |= get_group_members(ids[g])

        faltando = {u.lower() for u in obrigatorios} - membros
        if faltando:
            print(f" ❌ {grupos['MEMBROS']} está faltando {len(faltando)} usuários")
            for u in sorted(faltando):
                print(f"   - {u}")
                faltando_writer.writerow([grupos["MEMBROS"], u])
        else:
            print(f" ✅ {grupos['MEMBROS']} está completo")
            completos_writer.writerow([grupos["MEMBROS"]])
