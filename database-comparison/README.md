|  | Network access | User management | Storage layer | Sharding/partitioning<br/>(write scalability) | Read replicas<br/>(read scalability) | High availability<br/>(failover) | Encryption<br/>at rest | Encryption<br/>in transit |
|---|---|---|---|---|---|---|---|---|
| **Amazon ElastiCache for Memcached** [🏠][ecm1] | VPC [🔗][ecm6] | None | RAM of instance type | Optional; multi-node cluster [🍕][ecm5] | No [♊][ecm3] | No [🔥][ecm3] | No [🔒][ecm2] | Yes [🔒][ecm4] |
| **Amazon ElastiCache for Redis** [🏠][ecr1] | VPC | Database | RAM of instance type and EBS | Optional; see cluster mode enabled | Optional | Optional; see cluster mode enabled | Optional; KMS | Optional |
| **Amazon Redshift** [🏠][red1] | VPC | Database | Instance storage with SSD, HDD or RMS | Optional; see distribution style even or key | Optional; see distribution style all | Automatic restore from backup | Optional; KMS or HSM | Optional |
| **Amazon RDS** [🏠][rds1] | VPC | Database | EBS based | No | Optional | Optional; see Multi-AZFailover to secondary | Optional; KMS | Optional; parameter group |
| **Amazon Aurora** [🏠][aur1] | VPC or API | Database or IAM | Distributed storage volume with build-in replication | No | Optional | Failover to replicaFailover to primary with Multi-master | Optional; KMS | Optional; parameter group |
| **Amazon Neptune** [🏠][nep1] | VPC | Optional; SigV4 (IAM) | Distributed storage volume with build-in replication | No | Optional | Failover to replica | Optional; KMS | Yes |
| **Amazon DocumentDB for MongoDB** [🏠][doc1] | VPC | Database | Distributed storage volume with build-in replication | No | Optional | Failover to replica | Optional; KMS | Yes |
| **Amazon QLDB** [🏠][qld1] | API | IAM | Serverless | Currently only single strand journal supported | Build-in replication | Build-in HA | Yes; KMS | Yes |
| **Amazon DynamoDB** [🏠][ddb1] | API | IAM | Serverless; SSD | Build-in partitioning | Build-in replication | Build-in HA | Yes; KMS | Yes |
| **Amazon Timestream** [🏠][tim1] | API | IAM | Serverless; RAM and HHD | Build-in distribution | Build-in replication | Build-in HA | Yes; KMS | Yes |

[ecm1]: https://aws.amazon.com/elasticache/memcached/
[ecm2]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/Security.html
[ecm3]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/FaultTolerance.html
[ecm4]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/infrastructure-security.html
[ecm5]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/Clusters.AddNode.html
[ecm6]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/VPCs.html

[ecr1]: https://aws.amazon.com/elasticache/redis/

[red1]: https://aws.amazon.com/redshift/

[rds1]: https://aws.amazon.com/rds/

[aur1]: https://aws.amazon.com/rds/aurora/

[nep1]: https://aws.amazon.com/neptune/

[doc1]: https://aws.amazon.com/documentdb/

[qld1]: https://aws.amazon.com/qldb/

[ddb1]: https://aws.amazon.com/dynamodb/

[tim1]: https://aws.amazon.com/timestream/
