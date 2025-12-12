#### Étape 10.2: Vérifications

**CloudWatch Logs:**
- `/aws/lambda/fraud-scoring` → Voir les scores

**S3:**
- Attendre 2 minutes
- `raw/` → Fichiers .gz créés

**Email:**
- Vérifier alertes pour transactions BLOCKED/REVIEW

---

#### Étape 10.3: Lancer Crawler
**Glue → Crawlers → fraud-s3-crawler → Run**

Attendre 1-2 min → Status: **Completed**

---

#### Étape 10.4: Requêtes Athena
**Athena → Query editor**

Database: `frauddetectiondb`
```sql
-- Vue d'ensemble
SELECT 
    COUNT(*) as total_tx,
    ROUND(SUM(amount), 2) as total_amount,
    ROUND(AVG(amount), 2) as avg_amount,
    COUNT(DISTINCT user_id) as unique_users
FROM raw;

-- Top users
SELECT 
    user_id,
    COUNT(*) as tx_count,
    ROUND(SUM(amount), 2) as total
FROM raw
GROUP BY user_id
ORDER BY total DESC;

-- Transactions suspectes
SELECT 
    user_id,
    amount,
    merchant_id,
    device_id,
    timestamp
FROM raw
WHERE amount > 1000
ORDER BY amount DESC;

-- Analyse par catégorie
SELECT 
    merchant_category,
    COUNT(*) as count,
    ROUND(AVG(amount), 2) as avg_amount
FROM raw
GROUP BY merchant_category
ORDER BY count DESC;
```

---

## ✅ Checklist Finale

- [ ] KMS key créée
- [ ] Bucket S3 avec 3 dossiers
- [ ] 5 profils dans customer-profiles
- [ ] 4 règles dans fraud-rules
- [ ] SNS topic + email confirmé
- [ ] Kinesis Stream actif
- [ ] Firehose vers S3
- [ ] Rôle IAM créé
- [ ] Lambda ingestion déployée
- [ ] Lambda scoring déployée + trigger
- [ ] API Gateway déployé
- [ ] 50+ transactions envoyées
- [ ] Données dans S3
- [ ] Crawler exécuté
- [ ] Requêtes Athena OK
- [ ] Emails reçus

---

## 🧹 NETTOYAGE (Important!)

**Dans l'ordre:**

1. **Lambda** → Delete fraud-ingestion + fraud-scoring
2. **API Gateway** → Delete FraudDetectionAPI
3. **Kinesis Firehose** → Delete fraud-firehose-to-s3
4. **Kinesis Stream** → Delete fraud-detection-stream
5. **Glue Crawler** → Delete fraud-s3-crawler
6. **Glue Database** → Delete frauddetectiondb
7. **SNS** → Delete fraud-alerts
8. **DynamoDB** → Delete customer-profiles + fraud-rules
9. **S3** → Empty bucket → Delete bucket
10. **IAM Roles** → Delete FraudDetectionLambdaRole + AWSGlueServiceRole-FraudLab
11. **KMS** → Schedule key deletion (7 jours)

---

## 🎯 Pour Votre CV

**Titre:** Système de Détection de Fraude en Temps Réel - AWS

**Stack:** API Gateway • Lambda • Kinesis • S3 • DynamoDB • Athena • Glue • SNS • KMS • CloudWatch

**Résultats:**
- ⚡ Pipeline temps réel (<500ms)
- 🔒 Chiffrement bout-en-bout (KMS)
- 📊 Analytics SQL (Athena)
- 📧 Alerting automatique (SNS)
- 💰 Architecture serverless optimisée

---

## 📚 Compétences Démontrées

✅ **Data Engineering**: Streaming, Data Lake, ETL, Analytics SQL
✅ **Security**: KMS encryption, IAM policies, HTTPS
✅ **Architecture**: Serverless, Event-driven, Scalable
✅ **Monitoring**: CloudWatch Logs, Custom Metrics
✅ **Cost Optimization**: On-demand pricing, ~$0.48/lab

---

## 🔧 DEBUGGING & RÉSOLUTION DE PROBLÈMES

### **🐛 TOP 5 DES BUGS LES PLUS PROBABLES**

---

#### **BUG #-1: AccessDenied - CloudWatch Metrics** (Nouveau - Très fréquent)

**Symptôme:**