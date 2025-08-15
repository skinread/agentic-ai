# agent knowledge base
Write-Host "deploying knowledge base ..."
python prereqs/knowledge_base.py --mode create

# agent dynamodb
Write-Host "deploying DynamoDB ..."
python prereqs/dynamodb.py --mode create
