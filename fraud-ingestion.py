import json
import boto3
import os
from datetime import datetime
import uuid

kinesis = boto3.client('kinesis')
cloudwatch = boto3.client('cloudwatch')

STREAM_NAME = 'fraud-detection-stream'

def lambda_handler(event, context):
    try:
        # Parser le body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
        
        # Créer la transaction
        transaction = {
            'transaction_id': body.get('transaction_id', str(uuid.uuid4())),
            'user_id': body['user_id'],
            'amount': float(body['amount']),
            'merchant_id': body['merchant_id'],
            'merchant_category': body.get('merchant_category', 'UNKNOWN'),
            'device_id': body.get('device_id', 'unknown'),
            'location': body.get('location', 'unknown'),
            'timestamp': datetime.utcnow().isoformat(),
            'source_ip': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
        }
        
        print(f"✅ Transaction {transaction['transaction_id']} received")
        
        # Envoyer vers Kinesis
        response = kinesis.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps(transaction),
            PartitionKey=transaction['user_id']
        )
        
        # Métriques CloudWatch
        cloudwatch.put_metric_data(
            Namespace='FraudDetection',
            MetricData=[
                {
                    'MetricName': 'TransactionsIngested',
                    'Value': 1,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'TransactionAmount',
                    'Value': transaction['amount'],
                    'Unit': 'None'
                }
            ]
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Transaction received',
                'transaction_id': transaction['transaction_id']
            })
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }