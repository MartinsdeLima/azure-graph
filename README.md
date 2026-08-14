# script-azure

Script criado para retornar os grupos de um usuário no Azure AD, utilizando a API Microsoft Graph.

Além do script básico, aqui no README.md você encontrará alguns exemplos de como consultar dados de usuários e grupos utilizando a API Microsoft Graph executando diretamente o curl no terminal.

### Usando o script grupos_do_user.py

Faça o login no Azure CLI (necessário ter a CLI Azure instalada  ```bash sudo apt-get install azure-cli```):

```bash
az login --allow-no-subscriptions
```
Selecione uma `[Tenant and subscription selection]` ou precione enter para aceitar a default.

Sempre que for inicar uma sessão no terminal, execute o comando abaixo para exportar a variável de ambiente GRAPH_TOKEN:

```bash
export GRAPH_TOKEN=$(az account get-access-token --resource-type ms-graph --query accessToken -o tsv)
```

Executando o script:
```bash
python grupos_do_user.py nome.email@empresa.com
```

# Executando no terminal

### Json equivalente ao que o script grupos_do_user com name + id 
```bash
curl -s \
  -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/users/joao.silva@empresa.com/transitiveMemberOf?\$select=displayName,id" \
  | python3 -m json.tool
```

### Ou filtrando só os displayName com jq
```bash
curl -s \
  -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/users/joao.silva@empresa.com/transitiveMemberOf?\$select=displayName" \
  | jq -r '.value[].displayName' | sort
```
  ### Consultando dados de uma conta
```bash
  curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/users/nome.email@emprese.com.br?\$select=displayName,mail,jobTitle,department,officeLocation,mobilePhone,accountEnabled,createdDateTime,lastPasswordChangeDateTime" | python3 -m json.tool
```
  ### Trazer o id de um grupo
```bash
  curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/groups?\$filter=displayName%20eq%20'GRUPO_XPTO_MEMBROS'&\$select=id,displayName" \
  | python3 -m json.tool
````
  ### Pesquisar membros de um grupo pelo id do grupo
```bash
  curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/groups/{id}/transitiveMembers?\$select=displayName,userPrincipalName,accountEnabled" | python3 -m json.tool
  ```