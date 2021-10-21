# Database design considerations comparison

The [Planning and Designing Database on AWS](https://aws.amazon.com/training/classroom/planning-and-designing-databases-on-aws/) training goes into design considerations for many of the AWS database services. This table tries to summarize these considerations for easy comparison.

Last updated on `October 21, 2021`

| | Network access | Authentication & authorization | Partitioning<br/>(write scalability) | Read replicas<br/>(read scalability) | High availability<br/>(failover) | Encryption<br/>at rest | Encryption<br/>in transit |
|---|---|---|---|---|---|---|---|
| **Amazon ElastiCache for Memcached** [🏠][ecm1] | VPC [🔗][ecm2] | None | Optional; multi-node cluster [🍕][ecm4] | No | No [🔥][ecm6] | No [🔓][ecm7] | Yes [🔏][ecm8] |
| **Amazon ElastiCache for Redis** [🏠][ecr1] | VPC [🔗][ecr2] | Redis AUTH [🧍][ecr3a]<br/> or Redis RBAC [🧍][ecr3b] | Optional; cluster mode enabled [🍕][ecr4] | Optional [♊][ecr5] | Failover to replica [🧯][ecr6] | Optional; KMS [🔐][ecr7]| Optional [🔏][ecr8] |
| **Amazon Redshift** [🏠][red1] | VPC [🔗][red2] | Password, [🧍][red3a]<br> IAM or SAML [🧍][red3b] | Optional; distribution style EVEN or KEY [🍕][red4] | Optional; distribution style ALL [♊][red5] | Automatic restore from backup | Optional; KMS or HSM [🔐][red7] | Optional [🔏][red8] |
| **Amazon RDS** [🏠][rds1] | VPC [🔗][rds2] | Password, Kerberos or IAM [🧍][rds3] | No | Optional [♊][rds5] | Failover to secondary [🧯][rds6] | Optional; KMS [🔐][rds7] | Optional [🔏][rds8] |
| **Amazon Aurora** [🏠][aur1] | VPC [🔗][aur2] | Password, Kerberos or IAM [🧍][aur3] | No | Optional [♊][aur5] | Failover to replica [🧯][aur6a]<br/>or Multi-master [🧯][aur6b] | Optional; KMS [🔐][aur7] | Optional [🔏][aur8] |
| **Amazon Aurora Serverless** [🏠][asv1] | VPC [🔗][asv2a] or API [🖥️][asv2b] | Password, Kerberos or IAM [🧍][asv3] | No | Build-in replication [♊][asv5]| Build-in HA [🧯][asv6] | Optional; KMS [🔐][asv7] | Optional [🔏][asv8] |
| **Amazon Neptune** [🏠][nep1] | VPC [🔗][nep2] | Optional; IAM [🧍][nep3] | No | Optional [♊][nep5] | Failover to replica [🧯][nep6] | Optional; KMS [🔐][nep7] | Yes [🔏][nep8] |
| **Amazon DocumentDB (with MongoDB compatibility)** [🏠][doc1] | VPC [🔗][doc2] | Password [🧍][doc3] | No | Optional [♊][doc5] | Failover to replica [🧯][doc6] | Optional; KMS [🔐][doc7] | Yes [🔏][doc8] |
| **Amazon QLDB** [🏠][qld1] | API [🖥️][qld2] | IAM [🧍][qld3] | Currently only single strand journal supported [🍕][qld4] | Build-in replication [♊][qld5] | Build-in HA [🧯][qld6] | Yes; KMS [🔐][qld7] | Yes [🔏][qld8] |
| **Amazon DynamoDB** [🏠][ddb1] | API [🖥️][ddb2] | IAM [🧍][ddb3] | Build-in partitioning [🍕][ddb4] | Build-in replication [♊][ddb5] | Build-in HA [🧯][ddb6] | Yes; KMS [🔐][ddb7] | Yes [🔏][ddb8] |
| **Amazon Timestream** [🏠][tim1] | API [🖥️][tim2] | IAM [🧍][tim3] | Build-in distribution [🍕][tim4] | Build-in replication [♊][tim5] | Build-in HA [🧯][tim6] | Yes; KMS [🔐][tim7] | Yes [🔏][tim8] |

[ecm1]: https://aws.amazon.com/elasticache/memcached/
[ecm2]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/VPCs.html
[ecm4]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/Clusters.AddNode.html
[ecm6]: https://docs.aws.amazon.com/AmazonElastiCache/latest/mem-ug/FaultTolerance.html
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
[red3a]: https://docs.aws.amazon.com/redshift/latest/dg/r_Users.html
[red3b]: https://docs.aws.amazon.com/redshift/latest/mgmt/options-for-providing-iam-credentials.html
[red4]: https://docs.aws.amazon.com/redshift/latest/dg/c_choosing_dist_sort.html
[red5]: https://docs.aws.amazon.com/redshift/latest/dg/c_choosing_dist_sort.html
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
[aur2]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_VPC.html
[aur3]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/database-authentication.html
[aur5]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Replication.html
[aur6a]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html
[aur6b]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-multi-master.html
[aur7]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Overview.Encryption.html
[aur8]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.SSL.html

[asv1]: https://aws.amazon.com/rds/aurora/serverless/
[asv2a]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_VPC.html
[asv2b]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html
[asv3]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/database-authentication.html
[asv5]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.how-it-works.html
[asv6]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.how-it-works.html
[asv7]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Overview.Encryption.html
[asv8]: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.SSL.html

[nep1]: https://aws.amazon.com/neptune/
[nep2]: https://docs.aws.amazon.com/neptune/latest/userguide/security-vpc.html
[nep3]: https://docs.aws.amazon.com/neptune/latest/userguide/iam-auth-connecting.html
[nep5]: https://docs.aws.amazon.com/neptune/latest/userguide/manage-console-add-replicas.html
[nep6]: https://docs.aws.amazon.com/neptune/latest/apiref/API_FailoverDBCluster.html
[nep7]: https://docs.aws.amazon.com/neptune/latest/userguide/encrypt.html
[nep8]: https://docs.aws.amazon.com/neptune/latest/userguide/security-ssl.html

[doc1]: https://aws.amazon.com/documentdb/
[doc2]: https://docs.aws.amazon.com/documentdb/latest/developerguide/document-db-subnet-groups.html
[doc3]: https://docs.aws.amazon.com/documentdb/latest/developerguide/security.managing-users.html
[doc5]: https://docs.aws.amazon.com/documentdb/latest/developerguide/replication.html
[doc6]: https://docs.aws.amazon.com/documentdb/latest/developerguide/failover.html
[doc7]: https://docs.aws.amazon.com/documentdb/latest/developerguide/encryption-at-rest.html
[doc8]: https://docs.aws.amazon.com/documentdb/latest/developerguide/security.encryption.ssl.html

[qld1]: https://aws.amazon.com/qldb/
[qld2]: https://docs.aws.amazon.com/qldb/latest/developerguide/API_QLDB-Session_SendCommand.html
[qld3]: https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started-standard-mode.html
[qld4]: https://docs.aws.amazon.com/qldb/latest/developerguide/ledger-structure.html#ledger-structure.transactions
[qld5]: https://docs.aws.amazon.com/qldb/latest/developerguide/disaster-recovery-resiliency.html
[qld6]: https://docs.aws.amazon.com/qldb/latest/developerguide/disaster-recovery-resiliency.html
[qld7]: https://docs.aws.amazon.com/qldb/latest/developerguide/encryption-at-rest.html
[qld8]: https://docs.aws.amazon.com/qldb/latest/developerguide/encryption-in-transit.html

[ddb1]: https://aws.amazon.com/dynamodb/
[ddb2]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.API.html#HowItWorks.API.DataPlane
[ddb3]: https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondynamodb.html
[ddb4]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html#HowItWorks.CoreComponents.PrimaryKey
[ddb5]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html
[ddb6]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/disaster-recovery-resiliency.html
[ddb7]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/EncryptionAtRest.html
[ddb8]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/inter-network-traffic-privacy.html

[tim1]: https://aws.amazon.com/timestream/
[tim2]: https://docs.aws.amazon.com/timestream/latest/developerguide/API_Reference.html
[tim3]: https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontimestream.html
[tim4]: https://docs.aws.amazon.com/timestream/latest/developerguide/architecture.html
[tim5]: https://docs.aws.amazon.com/timestream/latest/developerguide/architecture.html
[tim6]: https://docs.aws.amazon.com/timestream/latest/developerguide/disaster-recovery-resiliency.html
[tim7]: https://docs.aws.amazon.com/timestream/latest/developerguide/EncryptionAtRest.html
[tim8]: https://docs.aws.amazon.com/timestream/latest/developerguide/EncryptionInTransit.html
