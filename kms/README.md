# KMS demos

A walk-through of key usages with commands for a quick demo.

Note that throughout the demo, we will use the `/tmp` directory, so we do not have to worry about cleaning up.

TODO: Create a CloudFormation template which creates the symmetric and asymmetric CMKs.

Source: https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-compare.html

# Symmetric key

First, we will need data to encrypt, so let's create a file
```sh
echo "Never gonna give you up" > /tmp/data.txt
```

Then, we encrypt that file. By default, KMS base64 encodes the response, so we'll decode it.
```sh
aws kms encrypt --key-id alias/demo/symmetric_key --plaintext fileb:///tmp/data.txt --output text --query CiphertextBlob | base64 --decode > /tmp/cipher.bin
```

And to decrypt it again we make another request to KMS, again base64 decoding the response. Note that we did not need to specify the key id.
```sh
aws kms decrypt --ciphertext-blob fileb:///tmp/cipher.bin --output text --query Plaintext | base64 --decode
```

# Generate data key

Instead of letting KMS doing the encryption and decryption, we can do it ourselves with a data key. When KMS generates a data key for us, we get the key in plain text (to encrypt with) and encrypted with the CMK (to store). Note that we cannot use `--query` since we need to retrieve two keys fromt he response. Therefore we use `jq` instead.
```sh
aws kms generate-data-key --key-id alias/demo/symmetric_key --key-spec AES_256 > /tmp/response.json
cat /tmp/response.json | jq ".CiphertextBlob" -r | base64 --decode > /tmp/key.bin
cat /tmp/response.json | jq ".Plaintext" -r | base64 --decode > /tmp/key.txt
```

We need some data (again).
```sh
echo "Never gonna let you down" > /tmp/data.txt
```

Now we can encrypt the data with our data key.
```sh
openssl enc -e -aes256 -kfile /tmp/key.txt -in /tmp/data.txt -out /tmp/data.bin
```

Lastly we will store the encrypted data (`data.bin`) and encrypted key (`key.bin`), but remove the plaintext data (`data.txt`) and plaintext key (`key.txt`)
```sh
shred -u -z -n 100 /tmp/response.json
shred -u -z -n 100 /tmp/data.txt
shred -u -z -n 100 /tmp/key.txt
```

Our data is safely stored. If we want to retrieve the plaintext again we can use KMS to decrypt our data key. And use that to decrypt our data.
```sh
aws kms decrypt --ciphertext-blob fileb:///tmp/key.bin --output text --query Plaintext | base64 --decode > /tmp/key.txt
openssl enc -d -aes256 -kfile /tmp/key.txt -in /tmp/data.bin
```

# Asymmetric key

For this demo, we will need our public key. We can retrieve it from KMS and share it with anyone. By default, KMS responds with a base64 encoded DER key. We'll just decode it and covert it to PEM.
```sh
aws kms get-public-key --key-id alias/demo/asymmetric_key --output text --query PublicKey | base64 --decode > /tmp/public.der
openssl rsa -pubin -inform DER -outform PEM -in /tmp/public.der -pubout -out /tmp/public.pem
```

Go ahead and share the public key with anyone.
```sh
cat /tmp/public.pem
```

Next, we will need a message to sign and verify. So here we create the message and store it for use.
```sh
echo "Never gonna run around and desert you" > /tmp/data.txt
```

Now that we have a message, we can sign it. Again, this is base64 encoded, so let's decode it before going further.
```sh
aws kms sign --key-id alias/demo/asymmetric_key --message-type RAW --signing-algorithm RSASSA_PKCS1_V1_5_SHA_512 --message fileb:///tmp/data.txt  --output text --query Signature | base64 --decode > /tmp/signature
```

Lastly we'll send both the message and the signature to someone. Since the already had our public key, they can now verify that the message was definitely sent by us; as only the owners of the private key in KMS could generate a signature that matches the public key.
```sh
openssl dgst -sha512 -verify /tmp/public.pem -signature /tmp/signature /tmp/message
```

Source: https://aws.amazon.com/blogs/security/how-to-verify-aws-kms-asymmetric-key-signatures-locally-with-openssl/
