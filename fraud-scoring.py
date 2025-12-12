import json
import boto3
import base64
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

CUSTOMER_TABLE = dynamodb.Table('customer-profiles')
SNS_TOPIC_ARN = 'VOTRE-ARN-SNS-ICI'  # ⚠️ MODIFIER

def lambda_handler(event, context):
    print(f"📦 Processing {len(event['Records'])} records")
    
    for record in event['Records']:
        try:
            # Décoder Kinesis
            payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            transaction = json.loads(payload)
            
            print(f"💳 Transaction: {transaction.get('transaction_id')}")
            
            # Enrichir
            enriched = enrich_transaction(transaction)
            
            # Scorer
            fraud_result = calculate_fraud_score(enriched)
            
            # Alerter
            handle_result(enriched, fraud_result)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            continue
    
    return {'statusCode': 200}

def enrich_transaction(transaction):
    """Enrichir avec profil client"""
    try:
        response = CUSTOMER_TABLE.get_item(Key={'user_id': transaction['user_id']})
        
        if 'Item' in response:
            profile = response['Item']
            transaction['customer_profile'] = {
                'avg_transaction_30d': float(profile.get('avg_transaction_30d', 0)),
                'transaction_count_30d': int(profile.get('transaction_count_30d', 0)),
                'last_device_id': profile.get('last_device_id', ''),
                'last_location': profile.get('last_location', ''),
                'risk_level': profile.get('risk_level', 'UNKNOWN'),
                'account_age_days': calculate_account_age(profile.get('account_created', ''))
            }
        else:
            transaction['customer_profile'] = {
                'avg_transaction_30d': 0,
                'transaction_count_30d': 0,
                'last_device_id': '',
                'last_location': '',
                'risk_level': 'NEW',
                'account_age_days': 0
            }
    except Exception as e:
        print(f"⚠️ Enrichment error: {str(e)}")
        transaction['customer_profile'] = {}
    
    return transaction

def calculate_fraud_score(transaction):
    """Calculer score de fraude"""
    score = 0
    triggered_rules = []
    
    profile = transaction.get('customer_profile', {})
    amount = transaction['amount']
    avg_30d = profile.get('avg_transaction_30d', 0)
    
    # Règle 1: Montant vs historique
    if avg_30d > 0 and amount > avg_30d * 5:
        score += 80
        triggered_rules.append('HIGH_AMOUNT_VS_HISTORY')
    
    # Règle 2: Montant absolu élevé
    if amount > 5000:
        score += 60
        triggered_rules.append('VERY_HIGH_AMOUNT')
    
    # Règle 3: Nouveau compte
    if profile.get('account_age_days', 999) < 7:
        score += 40
        triggered_rules.append('NEW_ACCOUNT')
    
    # Règle 4: Changement device
    if profile.get('last_device_id') and transaction.get('device_id') != profile.get('last_device_id'):
        score += 40
        triggered_rules.append('DEVICE_CHANGE')
    
    # Règle 5: Haute fréquence
    if profile.get('transaction_count_30d', 0) > 50:
        score += 30
        triggered_rules.append('HIGH_FREQUENCY')
    
    # Règle 6: Client à risque
    if profile.get('risk_level') == 'HIGH':
        score += 50
        triggered_rules.append('HIGH_RISK_CUSTOMER')
    
    final_score = min(score, 100)
    
    if final_score >= 80:
        decision = 'BLOCKED'
    elif final_score >= 50:
        decision = 'REVIEW'
    else:
        decision = 'APPROVED'
    
    print(f"  📊 Score: {final_score} → {decision}")
    
    return {
        'fraud_score': final_score,
        'decision': decision,
        'triggered_rules': triggered_rules
    }

def handle_result(transaction, fraud_result):
    """Alerter si suspect"""
    
    # Métriques
    try:
        cloudwatch.put_metric_data(
            Namespace='FraudDetection',
            MetricData=[
                {
                    'MetricName': 'FraudScore',
                    'Value': fraud_result['fraud_score'],
                    'Unit': 'None'
                },
                {
                    'MetricName': f"Transactions{fraud_result['decision']}",
                    'Value': 1,
                    'Unit': 'Count'
                }
            ]
        )
    except:
        pass
    
    # SNS Alert
    if fraud_result['decision'] in ['BLOCKED', 'REVIEW'] and SNS_TOPIC_ARN != 'VOTRE-ARN-SNS-ICI':
        try:
            message = {
                'transaction_id': transaction['transaction_id'],
                'user_id': transaction['user_id'],
                'amount': f"${transaction['amount']:.2f}",
                'fraud_score': fraud_result['fraud_score'],
                'decision': fraud_result['decision'],
                'rules': fraud_result['triggered_rules']
            }
            
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"🚨 Fraud Alert: {fraud_result['decision']}",
                Message=json.dumps(message, indent=2)
            )
        except Exception as e:
            print(f"⚠️ SNS error: {str(e)}")
    
    print(f"✅ {transaction['transaction_id']} | ${transaction['amount']:.2f} | {fraud_result['decision']}")

def calculate_account_age(created_date):
    """Calculer âge compte"""
    if not created_date:
        return 0
    try:
        created = datetime.fromisoformat(created_date)
        return (datetime.utcnow() - created).days
    except:
        return 0