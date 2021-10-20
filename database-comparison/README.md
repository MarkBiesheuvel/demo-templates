|  | Network access | Authentication & authorization | Partitioning<br/>(write scalability) | Read replicas<br/>(read scalability) | High availability<br/>(failover) | Encryption<br/>at rest | Encryption<br/>in transit |
|---|---|---|---|---|---|---|---|
| **Amazon ElastiCache for Memcached** [🏠][ecm1] | VPC [🔗][ecm2] | None | Optional; multi-node cluster [🍕][ecm4] | No [♊][ecm5] | No | No [🔐][ecm7] | Yes [🔏][ecm8] |
| **Amazon ElastiCache for Redis** [🏠][ecr1] | VPC [🔗][ecr2] | Redis AUTH [🧍][ecr3a]<br/> or Redis RBAC [🧍][ecr3b] | Optional; cluster mode enabled [🍕][ecr4] | Optional [♊][ecr5] | Failover to replica [🔥][ecr6] | Optional; KMS [🔐][ecr7]| Optional [🔏][ecr8] |
| **Amazon Redshift** [🏠][red1] | VPC [🔗][red2]  | Password [🧍][red3] | Optional; see distribution style EVEN or KEY [🍕][red4] | Optional; see distribution style ALL [♊][red4] | Automatic restore from backup | Optional; KMS or HSM [🔐][red7] | Optional [🔏][red8] |
| **Amazon RDS** [🏠][rds1] | VPC [🔗][rds2] | Password, Kerberos or IAM [🧍][rds3] |  No | Optional [♊][rds5] | Failover to secondary [🔥][rds6] | Optional; KMS [🔐][rds7] | Optional [🔏][rds8] |
| **Amazon Aurora** [🏠][aur1] | VPC [🔗][aur2a] or API [🔗][aur2b] | Password, Kerberos or IAM [🧍][aur3] | No | Optional [♊][aur5] | Failover to replica [🔥][aur6a]<br/>or Multi-master [🔥][aur6b] | Optional; KMS [🔐][aur7] | Optional [🔏][aur8] |
| **Amazon Neptune** [🏠][nep1] | VPC | Optional; SigV4 (IAM) | No | Optional | Failover to replica | Optional; KMS | Yes |
| **Amazon DocumentDB for MongoDB** [🏠][doc1] | VPC | Database | No | Optional | Failover to replica | Optional; KMS | Yes |
| **Amazon QLDB** [🏠][qld1] | API | IAM | Currently only single strand journal supported | Build-in replication | Build-in HA | Yes; KMS | Yes |
| **Amazon DynamoDB** [🏠][ddb1] | API | IAM | Build-in partitioning | Build-in replication | Build-in HA | Yes; KMS | Yes |
| **Amazon Timestream** [🏠][tim1] | API | IAM | Build-in distribution | Build-in replication | Build-in HA | Yes; KMS | Yes |

[ecm1]: https://aws.amazon.com/elasticache/memcached/
[ecm2]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/VPCs.html
[ecm4]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/Clusters.AddNode.html
[ecm5]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/FaultTolerance.html
[ecm7]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/Security.html
[ecm8]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/infrastructure-security.html

[ecr1]: https://aws.amazon.com/elasticache/redis/
[ecr2]: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/VPCs.html
[ecr3a]: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/auth.html
[ecr3b]: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Clusters.RBAC.html
[ecr4]: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Replication.Redis.Groups.html#Replication.Redis.Groups.Cluster
[ecr5]: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/increase-decrease-replica-count.html
[ecr6]: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/AutoFailover.html
[ecr7]: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/at-rest-encryption.html
[ecr8]: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/in-transit-encryption.html

[red1]: https://aws.amazon.com/redshift/
[red2]: https://docs.aws.amazon.com/redshift/latest/mgmt/managing-clusters-vpc.html
[red3]: https://docs.aws.amazon.com/redshift/latest/dg/r_Users.html
[red4]: https://docs.aws.amazon.com/redshift/latest/dg/c_choosing_dist_sort.html
[red7]: https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-db-encryption.html
[red8]: https://docs.aws.amazon.com/redshift/latest/mgmt/security-encryption-in-transit.html

[rds1]: https://aws.amazon.com/rds/
[rds2]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.html
[rds3]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/database-authentication.html
[rds5]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html
[rds6]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html
[rds7]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html
[rds8]: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html

[aur1]: https://aws.amazon.com/rds/aurora/
[aur2a]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_VPC.html
[aur2b]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html
[aur3]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/database-authentication.html
[aur5]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Replication.html
[aur6a]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html
[aur6b]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-multi-master.html
[aur7]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Overview.Encryption.html
[aur8]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.SSL.html

[nep1]: https://aws.amazon.com/neptune/

[doc1]: https://aws.amazon.com/documentdb/

[qld1]: https://aws.amazon.com/qldb/

[ddb1]: https://aws.amazon.com/dynamodb/

[tim1]: https://aws.amazon.com/timestream/
