/// Messenger Encryption Service
///
/// Client-side encryption for end-to-end encrypted messaging.
/// Compatible with UNIBOS backend encryption (X25519, AES-256-GCM, Ed25519).
///
/// Uses:
/// - X25519 for key exchange (Curve25519)
/// - AES-256-GCM for message encryption
/// - Ed25519 for message signing
/// - HKDF for key derivation

import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cryptography/cryptography.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Encryption service provider
final encryptionServiceProvider = Provider<EncryptionService>((ref) {
  return EncryptionService();
});

/// Key pair storage provider
final keyStorageProvider = Provider<KeyStorageService>((ref) {
  return KeyStorageService();
});

/// Encrypted message data
class EncryptedMessage {
  final Uint8List ciphertext;
  final Uint8List nonce;
  final Uint8List signature;
  final Uint8List senderPublicKey;
  final int encryptionVersion;

  EncryptedMessage({
    required this.ciphertext,
    required this.nonce,
    required this.signature,
    required this.senderPublicKey,
    this.encryptionVersion = 1,
  });

  /// Convert to JSON for API transmission
  Map<String, dynamic> toJson() {
    return {
      'ciphertext': base64Encode(ciphertext),
      'nonce': base64Encode(nonce),
      'signature': base64Encode(signature),
      'sender_public_key': base64Encode(senderPublicKey),
      'encryption_version': encryptionVersion,
    };
  }

  /// Create from JSON (API response)
  factory EncryptedMessage.fromJson(Map<String, dynamic> json) {
    return EncryptedMessage(
      ciphertext: base64Decode(json['ciphertext']),
      nonce: base64Decode(json['nonce']),
      signature: base64Decode(json['signature']),
      senderPublicKey: base64Decode(json['sender_public_key']),
      encryptionVersion: json['encryption_version'] ?? 1,
    );
  }

  /// Create from API message format
  factory EncryptedMessage.fromApiMessage({
    required String encryptedContent,
    required String contentNonce,
    required String signatureStr,
    required String senderKeyId,
  }) {
    return EncryptedMessage(
      ciphertext: base64Decode(encryptedContent),
      nonce: base64Decode(contentNonce),
      signature: base64Decode(signatureStr),
      senderPublicKey: Uint8List(0), // Will be fetched separately
    );
  }
}

/// User key pair for encryption
class UserKeyPair {
  final String keyId;
  final String deviceId;
  final Uint8List publicKey;
  final Uint8List privateKey;
  final Uint8List signingPublicKey;
  final Uint8List signingPrivateKey;
  final DateTime createdAt;
  final bool isPrimary;

  UserKeyPair({
    required this.keyId,
    required this.deviceId,
    required this.publicKey,
    required this.privateKey,
    required this.signingPublicKey,
    required this.signingPrivateKey,
    required this.createdAt,
    this.isPrimary = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'key_id': keyId,
      'device_id': deviceId,
      'public_key': base64Encode(publicKey),
      'private_key': base64Encode(privateKey),
      'signing_public_key': base64Encode(signingPublicKey),
      'signing_private_key': base64Encode(signingPrivateKey),
      'created_at': createdAt.toIso8601String(),
      'is_primary': isPrimary,
    };
  }

  factory UserKeyPair.fromJson(Map<String, dynamic> json) {
    return UserKeyPair(
      keyId: json['key_id'],
      deviceId: json['device_id'],
      publicKey: base64Decode(json['public_key']),
      privateKey: base64Decode(json['private_key']),
      signingPublicKey: base64Decode(json['signing_public_key']),
      signingPrivateKey: base64Decode(json['signing_private_key']),
      createdAt: DateTime.parse(json['created_at']),
      isPrimary: json['is_primary'] ?? false,
    );
  }
}

/// Encryption service for E2E messaging
class EncryptionService {
  // Algorithms
  final _x25519 = X25519();
  final _aesGcm = AesGcm.with256bits();
  final _ed25519 = Ed25519();
  final _hkdf = Hkdf(hmac: Hmac.sha256(), outputLength: 32);

  // Constants
  static const int nonceSize = 12;
  static const int keySize = 32;
  static const messageKeyInfo = 'messenger-v1';
  static const groupKeyInfo = 'group-key-v1';

  /// Generate X25519 key pair for encryption
  Future<SimpleKeyPair> generateX25519KeyPair() async {
    return await _x25519.newKeyPair();
  }

  /// Generate Ed25519 key pair for signing
  Future<SimpleKeyPair> generateEd25519KeyPair() async {
    return await _ed25519.newKeyPair();
  }

  /// Generate complete user key pairs (encryption + signing)
  Future<UserKeyPair> generateUserKeyPairs({
    required String keyId,
    required String deviceId,
    bool isPrimary = false,
  }) async {
    final encryptionPair = await generateX25519KeyPair();
    final signingPair = await generateEd25519KeyPair();

    final encryptionPublic = await encryptionPair.extractPublicKey();
    final encryptionPrivate = await encryptionPair.extractPrivateKeyBytes();
    final signingPublic = await signingPair.extractPublicKey();
    final signingPrivate = await signingPair.extractPrivateKeyBytes();

    return UserKeyPair(
      keyId: keyId,
      deviceId: deviceId,
      publicKey: Uint8List.fromList(encryptionPublic.bytes),
      privateKey: Uint8List.fromList(encryptionPrivate),
      signingPublicKey: Uint8List.fromList(signingPublic.bytes),
      signingPrivateKey: Uint8List.fromList(signingPrivate),
      createdAt: DateTime.now(),
      isPrimary: isPrimary,
    );
  }

  /// Derive shared secret using X25519 key exchange
  Future<SecretKey> deriveSharedSecret(
    Uint8List privateKey,
    Uint8List peerPublicKey,
  ) async {
    final myPrivate = SimpleKeyPairData(
      privateKey,
      publicKey: SimplePublicKey(Uint8List(32), type: KeyPairType.x25519),
      type: KeyPairType.x25519,
    );

    final theirPublic = SimplePublicKey(peerPublicKey, type: KeyPairType.x25519);

    return await _x25519.sharedSecretKey(
      keyPair: myPrivate,
      remotePublicKey: theirPublic,
    );
  }

  /// Derive message key using HKDF
  Future<SecretKey> deriveMessageKey(
    SecretKey sharedSecret, {
    String info = messageKeyInfo,
  }) async {
    return await _hkdf.deriveKey(
      secretKey: sharedSecret,
      info: utf8.encode(info),
      nonce: Uint8List(0),
    );
  }

  /// Encrypt a message
  Future<EncryptedMessage> encryptMessage({
    required String plaintext,
    required Uint8List senderPrivateKey,
    required Uint8List recipientPublicKey,
    required Uint8List signingPrivateKey,
    Uint8List? associatedData,
  }) async {
    // Derive shared secret and message key
    final sharedSecret = await deriveSharedSecret(senderPrivateKey, recipientPublicKey);
    final messageKey = await deriveMessageKey(sharedSecret);

    // Generate random nonce
    final nonce = _aesGcm.newNonce();

    // Encrypt with AES-256-GCM
    final plaintextBytes = utf8.encode(plaintext);
    final secretBox = await _aesGcm.encrypt(
      plaintextBytes,
      secretKey: messageKey,
      nonce: nonce,
      aad: associatedData ?? Uint8List(0),
    );

    // Combine ciphertext and MAC tag
    final ciphertext = Uint8List.fromList([
      ...secretBox.cipherText,
      ...secretBox.mac.bytes,
    ]);

    // Sign the message (nonce + ciphertext)
    final signatureData = Uint8List.fromList([
      ...nonce,
      ...ciphertext,
      if (associatedData != null) ...associatedData,
    ]);

    final signingKeyPair = SimpleKeyPairData(
      signingPrivateKey,
      publicKey: SimplePublicKey(Uint8List(32), type: KeyPairType.ed25519),
      type: KeyPairType.ed25519,
    );

    final signature = await _ed25519.sign(signatureData, keyPair: signingKeyPair);

    // Get sender's public key
    final senderKeyPair = SimpleKeyPairData(
      senderPrivateKey,
      publicKey: SimplePublicKey(Uint8List(32), type: KeyPairType.x25519),
      type: KeyPairType.x25519,
    );
    final senderPublicKey = await senderKeyPair.extractPublicKey();

    return EncryptedMessage(
      ciphertext: ciphertext,
      nonce: Uint8List.fromList(nonce),
      signature: Uint8List.fromList(signature.bytes),
      senderPublicKey: Uint8List.fromList(senderPublicKey.bytes),
    );
  }

  /// Decrypt a message
  Future<String> decryptMessage({
    required EncryptedMessage encryptedMessage,
    required Uint8List recipientPrivateKey,
    required Uint8List senderPublicKey,
    required Uint8List senderSigningPublicKey,
    Uint8List? associatedData,
  }) async {
    // Verify signature first
    final signatureData = Uint8List.fromList([
      ...encryptedMessage.nonce,
      ...encryptedMessage.ciphertext,
      if (associatedData != null) ...associatedData,
    ]);

    final signingPublic = SimplePublicKey(
      senderSigningPublicKey,
      type: KeyPairType.ed25519,
    );

    final signature = Signature(
      encryptedMessage.signature,
      publicKey: signingPublic,
    );

    final isValid = await _ed25519.verify(signatureData, signature: signature);
    if (!isValid) {
      throw Exception('Message signature verification failed');
    }

    // Derive shared secret and message key
    final sharedSecret = await deriveSharedSecret(recipientPrivateKey, senderPublicKey);
    final messageKey = await deriveMessageKey(sharedSecret);

    // Split ciphertext and MAC tag
    final ciphertext = encryptedMessage.ciphertext;
    final macStartIndex = ciphertext.length - 16; // AES-GCM MAC is 16 bytes
    final actualCiphertext = ciphertext.sublist(0, macStartIndex);
    final macBytes = ciphertext.sublist(macStartIndex);

    // Decrypt with AES-256-GCM
    final secretBox = SecretBox(
      actualCiphertext,
      nonce: encryptedMessage.nonce,
      mac: Mac(macBytes),
    );

    final plaintextBytes = await _aesGcm.decrypt(
      secretBox,
      secretKey: messageKey,
      aad: associatedData ?? Uint8List(0),
    );

    return utf8.decode(plaintextBytes);
  }

  /// Generate random group key
  Uint8List generateGroupKey() {
    return Uint8List.fromList(_aesGcm.newSecretKey().toString().codeUnits.take(keySize).toList());
  }

  /// Encrypt group key for a recipient
  Future<Uint8List> encryptGroupKey({
    required Uint8List groupKey,
    required Uint8List recipientPublicKey,
    required Uint8List senderPrivateKey,
  }) async {
    final sharedSecret = await deriveSharedSecret(senderPrivateKey, recipientPublicKey);
    final keyEncryptionKey = await deriveMessageKey(sharedSecret, info: groupKeyInfo);

    final nonce = _aesGcm.newNonce();
    final secretBox = await _aesGcm.encrypt(
      groupKey,
      secretKey: keyEncryptionKey,
      nonce: nonce,
    );

    return Uint8List.fromList([
      ...nonce,
      ...secretBox.cipherText,
      ...secretBox.mac.bytes,
    ]);
  }

  /// Decrypt group key
  Future<Uint8List> decryptGroupKey({
    required Uint8List encryptedGroupKey,
    required Uint8List senderPublicKey,
    required Uint8List recipientPrivateKey,
  }) async {
    final nonce = encryptedGroupKey.sublist(0, nonceSize);
    final ciphertext = encryptedGroupKey.sublist(nonceSize, encryptedGroupKey.length - 16);
    final macBytes = encryptedGroupKey.sublist(encryptedGroupKey.length - 16);

    final sharedSecret = await deriveSharedSecret(recipientPrivateKey, senderPublicKey);
    final keyEncryptionKey = await deriveMessageKey(sharedSecret, info: groupKeyInfo);

    final secretBox = SecretBox(ciphertext, nonce: nonce, mac: Mac(macBytes));

    final groupKey = await _aesGcm.decrypt(secretBox, secretKey: keyEncryptionKey);
    return Uint8List.fromList(groupKey);
  }

  /// Encrypt with group key
  Future<EncryptedMessage> encryptWithGroupKey({
    required String plaintext,
    required Uint8List groupKey,
    required Uint8List signingPrivateKey,
  }) async {
    final nonce = _aesGcm.newNonce();
    final secretKey = SecretKey(groupKey);

    final plaintextBytes = utf8.encode(plaintext);
    final secretBox = await _aesGcm.encrypt(
      plaintextBytes,
      secretKey: secretKey,
      nonce: nonce,
    );

    final ciphertext = Uint8List.fromList([
      ...secretBox.cipherText,
      ...secretBox.mac.bytes,
    ]);

    // Sign
    final signatureData = Uint8List.fromList([...nonce, ...ciphertext]);
    final signingKeyPair = SimpleKeyPairData(
      signingPrivateKey,
      publicKey: SimplePublicKey(Uint8List(32), type: KeyPairType.ed25519),
      type: KeyPairType.ed25519,
    );
    final signature = await _ed25519.sign(signatureData, keyPair: signingKeyPair);

    return EncryptedMessage(
      ciphertext: ciphertext,
      nonce: Uint8List.fromList(nonce),
      signature: Uint8List.fromList(signature.bytes),
      senderPublicKey: Uint8List(0),
    );
  }

  /// Decrypt with group key
  Future<String> decryptWithGroupKey({
    required EncryptedMessage encryptedMessage,
    required Uint8List groupKey,
    required Uint8List senderSigningPublicKey,
  }) async {
    // Verify signature
    final signatureData = Uint8List.fromList([
      ...encryptedMessage.nonce,
      ...encryptedMessage.ciphertext,
    ]);

    final signingPublic = SimplePublicKey(
      senderSigningPublicKey,
      type: KeyPairType.ed25519,
    );

    final signature = Signature(
      encryptedMessage.signature,
      publicKey: signingPublic,
    );

    final isValid = await _ed25519.verify(signatureData, signature: signature);
    if (!isValid) {
      throw Exception('Message signature verification failed');
    }

    // Decrypt
    final ciphertext = encryptedMessage.ciphertext;
    final macStartIndex = ciphertext.length - 16;
    final actualCiphertext = ciphertext.sublist(0, macStartIndex);
    final macBytes = ciphertext.sublist(macStartIndex);

    final secretKey = SecretKey(groupKey);
    final secretBox = SecretBox(
      actualCiphertext,
      nonce: encryptedMessage.nonce,
      mac: Mac(macBytes),
    );

    final plaintextBytes = await _aesGcm.decrypt(secretBox, secretKey: secretKey);
    return utf8.decode(plaintextBytes);
  }

  /// Hash content (SHA-256)
  Future<String> hashContent(Uint8List content) async {
    final hash = await Sha256().hash(content);
    return hash.bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
  }
}

/// Secure key storage service
class KeyStorageService {
  final _storage = const FlutterSecureStorage();

  static const _keyPrefix = 'messenger_key_';
  static const _primaryKeyId = 'messenger_primary_key_id';

  /// Store user key pair
  Future<void> storeKeyPair(UserKeyPair keyPair) async {
    final json = jsonEncode(keyPair.toJson());
    await _storage.write(key: '$_keyPrefix${keyPair.keyId}', value: json);

    if (keyPair.isPrimary) {
      await _storage.write(key: _primaryKeyId, value: keyPair.keyId);
    }
  }

  /// Get key pair by ID
  Future<UserKeyPair?> getKeyPair(String keyId) async {
    final json = await _storage.read(key: '$_keyPrefix$keyId');
    if (json == null) return null;
    return UserKeyPair.fromJson(jsonDecode(json));
  }

  /// Get primary key pair
  Future<UserKeyPair?> getPrimaryKeyPair() async {
    final keyId = await _storage.read(key: _primaryKeyId);
    if (keyId == null) return null;
    return getKeyPair(keyId);
  }

  /// Delete key pair
  Future<void> deleteKeyPair(String keyId) async {
    await _storage.delete(key: '$_keyPrefix$keyId');
  }

  /// List all stored key IDs
  Future<List<String>> listKeyIds() async {
    final all = await _storage.readAll();
    return all.keys
        .where((k) => k.startsWith(_keyPrefix))
        .map((k) => k.substring(_keyPrefix.length))
        .toList();
  }

  /// Clear all keys
  Future<void> clearAllKeys() async {
    final keyIds = await listKeyIds();
    for (final keyId in keyIds) {
      await deleteKeyPair(keyId);
    }
    await _storage.delete(key: _primaryKeyId);
  }
}
