# KMS demos

A walk-through of key usages with commands for a quick demo.

# Symmetric key

TODO

# Asymmetric key

For this demo, we will need our public key. We can retrieve it from KMS and share it with anyone. By default, KMS responds with a base64 encoded DER key. We'll just decode it and covert it to PEM.
```sh
aws kms get-public-key --key-id alias/asymmetric_demo --output text --query PublicKey | base64 --decode > /tmp/public.der
openssl rsa -pubin -inform DER -outform PEM -in /tmp/public.der -pubout -out /tmp/public.pem
```

Go ahead and share the public key with anyone.
```sh
cat /tmp/public.pem
```

Next, we will need a message to sign and verify. So here we create the message and store it for use. Note that throughout the demo, we will use the `/tmp` directory, so we do not have to worry about cleaning up.
```sh
echo "Never gonna give you up" > /tmp/message
```

Now that we have a message, we can sign it. Again, this is base64 encoded, so let's decode it before going further.
```sh
aws kms sign --key-id alias/asymmetric_demo --message-type RAW --signing-algorithm RSASSA_PKCS1_V1_5_SHA_512 --message fileb:///tmp/message  --output text --query Signature | base64 --decode > /tmp/signature
```

Lastly we'll send both the message and the signature to someone. Since the already had our public key, they can now verify that the message was definitely sent by us; as only the owners of the private key in KMS could generate a signature that matches the public key.
```sh
openssl dgst -sha512 -verify /tmp/public.pem -signature /tmp/signature /tmp/message
```

Source: https://aws.amazon.com/blogs/security/how-to-verify-aws-kms-asymmetric-key-signatures-locally-with-openssl/
