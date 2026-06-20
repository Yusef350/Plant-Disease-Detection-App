# 🌿 Flutter Frontend Integration Guide

> Complete guide to connect your Flutter app with the Plant Disease Detection backend API.

---

## Table of Contents

1. [Setup & Dependencies](#1-setup--dependencies)
2. [Project Structure](#2-project-structure)
3. [API Client (Core)](#3-api-client-core)
4. [Models (Data Layer)](#4-models-data-layer)
5. [Auth Service](#5-auth-service)
6. [Scan Service](#6-scan-service)
7. [Disease Service](#7-disease-service)
8. [User Service](#8-user-service)
9. [Screen-by-Screen Integration](#9-screen-by-screen-integration)
10. [Error Handling & Edge Cases](#10-error-handling--edge-cases)
11. [State Management (Riverpod)](#11-state-management-riverpod)
12. [Image Upload Flow](#12-image-upload-flow)

---

## 1. Setup & Dependencies

### pubspec.yaml

```yaml
dependencies:
  flutter:
    sdk: flutter

  # Networking
  dio: ^5.4.0 # HTTP client (better than http for file uploads)

  # State Management
  flutter_riverpod: ^2.5.1 # Preferred state management
  riverpod_annotation: ^2.3.5

  # Local Storage
  flutter_secure_storage: ^9.2.2 # Store JWT token securely
  shared_preferences: ^2.3.0 # Non-sensitive settings

  # Image
  image_picker: ^1.1.2 # Camera / gallery picker
  cached_network_image: ^3.4.1 # Image caching

  # UI Helpers
  intl: ^0.19.0 # Date formatting
  shimmer: ^3.0.0 # Loading skeletons
  lottie: ^3.1.0 # Animated loaders
```

Run:

```bash
flutter pub get
```

---

## 2. Project Structure

```
lib/
├── main.dart
│
├── core/
│   ├── constants/
│   │   └── api_constants.dart      # Base URL, endpoints
│   ├── network/
│   │   ├── api_client.dart         # Dio setup + interceptors
│   │   └── api_exceptions.dart     # Custom exceptions
│   └── storage/
│       └── secure_storage.dart     # Token persistence
│
├── data/
│   ├── models/
│   │   ├── user_model.dart
│   │   ├── scan_model.dart
│   │   ├── diagnosis_model.dart
│   │   ├── disease_model.dart
│   │   └── api_response.dart
│   ├── repositories/
│   │   ├── auth_repository.dart
│   │   ├── scan_repository.dart
│   │   ├── disease_repository.dart
│   │   └── user_repository.dart
│   └── providers/
│       ├── auth_provider.dart
│       ├── scan_provider.dart
│       ├── disease_provider.dart
│       └── user_provider.dart
│
├── presentation/
│   ├── screens/
│   │   ├── splash/
│   │   ├── onboarding/
│   │   ├── auth/
│   │   │   ├── login_screen.dart
│   │   │   └── register_screen.dart
│   │   ├── home/
│   │   ├── scan/
│   │   │   ├── camera_screen.dart
│   │   │   ├── preview_screen.dart
│   │   │   ├── processing_screen.dart
│   │   │   └── result_screen.dart
│   │   ├── diseases/
│   │   │   ├── disease_list_screen.dart
│   │   │   └── disease_detail_screen.dart
│   │   ├── history/
│   │   ├── profile/
│   │   └── settings/
│   └── widgets/
│       ├── loading_widget.dart
│       ├── error_widget.dart
│       └── scan_card.dart
│
└── utils/
    ├── date_formatter.dart
    └── validators.dart
```

---

## 3. API Client (Core)

### `lib/core/constants/api_constants.dart`

```dart
class ApiConstants {
  // Change this to your server IP
  // For Android emulator use: 10.0.2.2
  // For iOS simulator use: 127.0.0.1
  // For physical device use: your PC's local IP (e.g. 192.168.1.3)
  static const String baseUrl = 'http://10.0.2.2:5000';

  // Auth
  static const String register = '/api/auth/register';
  static const String login    = '/api/auth/login';
  static const String me       = '/api/auth/me';

  // Scans
  static const String scans    = '/api/scans';

  // Diseases
  static const String diseases = '/api/diseases';

  // User
  static const String profile  = '/api/users/profile';
  static const String password = '/api/users/password';

  // Health
  static const String health   = '/api/health';
}
```

### `lib/core/storage/secure_storage.dart`

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorage {
  static const _storage = FlutterSecureStorage();
  static const _tokenKey = 'jwt_token';
  static const _userIdKey = 'user_id';

  // ── Token ───────────────────────────────────────────
  static Future<void> saveToken(String token) async {
    await _storage.write(key: _tokenKey, value: token);
  }

  static Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  static Future<void> deleteToken() async {
    await _storage.delete(key: _tokenKey);
  }

  // ── User ID ─────────────────────────────────────────
  static Future<void> saveUserId(String id) async {
    await _storage.write(key: _userIdKey, value: id);
  }

  static Future<String?> getUserId() async {
    return await _storage.read(key: _userIdKey);
  }

  // ── Clear all ───────────────────────────────────────
  static Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}
```

### `lib/core/network/api_exceptions.dart`

```dart
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, {this.statusCode});

  @override
  String toString() => message;

  // ── Factory helpers ─────────────────────────────────
  factory ApiException.fromStatusCode(int code, String body) {
    switch (code) {
      case 400: return ApiException('Invalid request: $body', statusCode: 400);
      case 401: return ApiException('Unauthorized — please log in again', statusCode: 401);
      case 403: return ApiException('Access denied', statusCode: 403);
      case 404: return ApiException('Not found', statusCode: 404);
      case 409: return ApiException('Already exists: $body', statusCode: 409);
      case 413: return ApiException('File too large (max 16 MB)', statusCode: 413);
      case 500: return ApiException('Server error — try again later', statusCode: 500);
      default:  return ApiException('Something went wrong ($code)', statusCode: code);
    }
  }
}

class NoInternetException extends ApiException {
  NoInternetException() : super('No internet connection');
}
```

### `lib/core/network/api_client.dart`

```dart
import 'dart:io';
import 'package:dio/dio.dart';
import '../constants/api_constants.dart';
import '../storage/secure_storage.dart';
import 'api_exceptions.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;

  late final Dio _dio;

  ApiClient._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // ── Request interceptor: attach JWT ─────────────
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await SecureStorage.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        handler.next(error);
      },
    ));
  }

  // ── GET ───────────────────────────────────────────────
  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParams,
  }) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParams);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ── POST (JSON) ──────────────────────────────────────
  Future<Map<String, dynamic>> post(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _dio.post(path, data: data);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ── PUT (JSON) ───────────────────────────────────────
  Future<Map<String, dynamic>> put(
    String path, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final response = await _dio.put(path, data: data);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ── POST (multipart — file upload) ──────────────────
  Future<Map<String, dynamic>> uploadFile(
    String path, {
    required File file,
    String fieldName = 'image',
    void Function(int, int)? onProgress,
  }) async {
    try {
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(
          file.path,
          filename: file.path.split('/').last,
        ),
      });

      final response = await _dio.post(
        path,
        data: formData,
        onSendProgress: onProgress,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ── Error handler ────────────────────────────────────
  ApiException _handleError(DioException e) {
    if (e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.connectionTimeout) {
      return NoInternetException();
    }

    final response = e.response;
    if (response != null) {
      final body = response.data;
      final message = body is Map ? (body['error'] ?? 'Unknown error') : '$body';
      return ApiException.fromStatusCode(response.statusCode ?? 500, message);
    }

    return ApiException('Connection failed: ${e.message}');
  }
}
```

---

## 4. Models (Data Layer)

### `lib/data/models/user_model.dart`

```dart
class UserModel {
  final String id;
  final String email;
  final String displayName;
  final String role;
  final DateTime? createdAt;
  final DateTime? lastLoginAt;

  UserModel({
    required this.id,
    required this.email,
    required this.displayName,
    this.role = 'user',
    this.createdAt,
    this.lastLoginAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      displayName: json['displayName'] ?? '',
      role: json['role'] ?? 'user',
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'].toString())
          : null,
      lastLoginAt: json['lastLoginAt'] != null
          ? DateTime.tryParse(json['lastLoginAt'].toString())
          : null,
    );
  }
}

class AuthResponse {
  final UserModel user;
  final String token;

  AuthResponse({required this.user, required this.token});

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      user: UserModel.fromJson(json['user']),
      token: json['token'],
    );
  }
}

class UserStats {
  final int totalScans;
  final MostDetectedDisease? mostDetectedDisease;

  UserStats({required this.totalScans, this.mostDetectedDisease});

  factory UserStats.fromJson(Map<String, dynamic> json) {
    return UserStats(
      totalScans: json['totalScans'] ?? 0,
      mostDetectedDisease: json['mostDetectedDisease'] != null
          ? MostDetectedDisease.fromJson(json['mostDetectedDisease'])
          : null,
    );
  }
}

class MostDetectedDisease {
  final String diseaseName;
  final int count;

  MostDetectedDisease({required this.diseaseName, required this.count});

  factory MostDetectedDisease.fromJson(Map<String, dynamic> json) {
    return MostDetectedDisease(
      diseaseName: json['disease']?['name'] ?? 'Unknown',
      count: json['count'] ?? 0,
    );
  }
}
```

### `lib/data/models/disease_model.dart`

```dart
class DiseaseModel {
  final String id;
  final String name;
  final String description;
  final String symptoms;
  final String causes;
  final String treatment;
  final String prevention;
  final String severity;
  final String? imageUrl;

  DiseaseModel({
    required this.id,
    required this.name,
    required this.description,
    required this.symptoms,
    required this.causes,
    required this.treatment,
    required this.prevention,
    required this.severity,
    this.imageUrl,
  });

  factory DiseaseModel.fromJson(Map<String, dynamic> json) {
    return DiseaseModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      symptoms: json['symptoms'] ?? '',
      causes: json['causes'] ?? '',
      treatment: json['treatment'] ?? '',
      prevention: json['prevention'] ?? '',
      severity: json['severity'] ?? 'medium',
      imageUrl: json['imageUrl'],
    );
  }

  /// "Tomato___Late_blight" → "Late blight"
  String get displayDiseaseName {
    final parts = name.split('___');
    if (parts.length > 1) {
      return parts[1].replaceAll('_', ' ');
    }
    return name.replaceAll('_', ' ');
  }

  /// "Tomato___Late_blight" → "Tomato"
  String get plantName {
    return name.split('___').first.replaceAll('_', ' ');
  }

  bool get isHealthy => name.toLowerCase().contains('healthy');
}
```

### `lib/data/models/scan_model.dart`

```dart
import 'disease_model.dart';

class ScanModel {
  final String id;
  final String imageUrl;
  final String status;
  final DateTime? createdAt;
  final DiagnosisModel? diagnosis;
  final DiseaseModel? disease;

  ScanModel({
    required this.id,
    required this.imageUrl,
    required this.status,
    this.createdAt,
    this.diagnosis,
    this.disease,
  });

  factory ScanModel.fromJson(Map<String, dynamic> json) {
    return ScanModel(
      id: json['id'] ?? '',
      imageUrl: json['imageUrl'] ?? '',
      status: json['status'] ?? 'unknown',
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'].toString())
          : null,
      diagnosis: json['diagnosis'] != null
          ? DiagnosisModel.fromJson(json['diagnosis'])
          : null,
      disease: json['disease'] != null
          ? DiseaseModel.fromJson(json['disease'])
          : null,
    );
  }
}

class DiagnosisModel {
  final String id;
  final double confidence;
  final bool isHealthy;
  final DateTime? createdAt;

  DiagnosisModel({
    required this.id,
    required this.confidence,
    required this.isHealthy,
    this.createdAt,
  });

  factory DiagnosisModel.fromJson(Map<String, dynamic> json) {
    return DiagnosisModel(
      id: json['id'] ?? '',
      confidence: (json['confidence'] ?? 0).toDouble(),
      isHealthy: json['isHealthy'] ?? false,
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'].toString())
          : null,
    );
  }

  /// e.g. "97.2%"
  String get confidencePercent =>
      '${(confidence * 100).toStringAsFixed(1)}%';
}

class PredictionModel {
  final String className;
  final String plantName;
  final String diseaseName;
  final double confidence;
  final bool isHealthy;

  PredictionModel({
    required this.className,
    required this.plantName,
    required this.diseaseName,
    required this.confidence,
    required this.isHealthy,
  });

  factory PredictionModel.fromJson(Map<String, dynamic> json) {
    return PredictionModel(
      className: json['className'] ?? '',
      plantName: json['plantName'] ?? '',
      diseaseName: json['diseaseName'] ?? '',
      confidence: (json['confidence'] ?? 0).toDouble(),
      isHealthy: json['isHealthy'] ?? false,
    );
  }

  String get confidencePercent =>
      '${(confidence * 100).toStringAsFixed(1)}%';
}

/// Full result returned from POST /api/scans
class ScanResultModel {
  final ScanModel scan;
  final DiagnosisModel diagnosis;
  final PredictionModel prediction;
  final DiseaseModel? disease;

  ScanResultModel({
    required this.scan,
    required this.diagnosis,
    required this.prediction,
    this.disease,
  });

  factory ScanResultModel.fromJson(Map<String, dynamic> json) {
    return ScanResultModel(
      scan: ScanModel.fromJson(json['scan']),
      diagnosis: DiagnosisModel.fromJson(json['diagnosis']),
      prediction: PredictionModel.fromJson(json['prediction']),
      disease: json['disease'] != null
          ? DiseaseModel.fromJson(json['disease'])
          : null,
    );
  }
}
```

---

## 5. Auth Service

### `lib/data/repositories/auth_repository.dart`

```dart
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../../core/storage/secure_storage.dart';
import '../models/user_model.dart';

class AuthRepository {
  final _api = ApiClient();

  /// Register a new user → saves token automatically
  Future<AuthResponse> register({
    required String displayName,
    required String email,
    required String password,
  }) async {
    final data = await _api.post(ApiConstants.register, data: {
      'displayName': displayName,
      'email': email,
      'password': password,
    });

    final auth = AuthResponse.fromJson(data);
    await SecureStorage.saveToken(auth.token);
    await SecureStorage.saveUserId(auth.user.id);
    return auth;
  }

  /// Login → saves token automatically
  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final data = await _api.post(ApiConstants.login, data: {
      'email': email,
      'password': password,
    });

    final auth = AuthResponse.fromJson(data);
    await SecureStorage.saveToken(auth.token);
    await SecureStorage.saveUserId(auth.user.id);
    return auth;
  }

  /// Get current user (validates token is still valid)
  Future<UserModel> getCurrentUser() async {
    final data = await _api.get(ApiConstants.me);
    return UserModel.fromJson(data['user']);
  }

  /// Logout — clear stored token
  Future<void> logout() async {
    await SecureStorage.clearAll();
  }

  /// Check if user is logged in
  Future<bool> isLoggedIn() async {
    final token = await SecureStorage.getToken();
    return token != null && token.isNotEmpty;
  }
}
```

### Screen Integration — Login

```dart
class LoginScreen extends ConsumerStatefulWidget { ... }

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailCtrl    = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _formKey      = GlobalKey<FormState>();
  bool _loading = false;
  String? _error;

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() { _loading = true; _error = null; });

    try {
      final auth = await AuthRepository().login(
        email: _emailCtrl.text.trim(),
        password: _passwordCtrl.text,
      );
      // Navigate to home
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } on ApiException catch (e) {
      setState(() { _error = e.message; });
    } finally {
      setState(() { _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            TextFormField(
              controller: _emailCtrl,
              decoration: const InputDecoration(labelText: 'Email'),
              validator: (v) =>
                  v != null && v.contains('@') ? null : 'Enter a valid email',
            ),
            TextFormField(
              controller: _passwordCtrl,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Password'),
              validator: (v) =>
                  v != null && v.length >= 6 ? null : 'Min 6 characters',
            ),
            if (_error != null)
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ElevatedButton(
              onPressed: _loading ? null : _handleLogin,
              child: _loading
                  ? const CircularProgressIndicator()
                  : const Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 6. Scan Service

### `lib/data/repositories/scan_repository.dart`

```dart
import 'dart:io';
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../models/scan_model.dart';

class ScanRepository {
  final _api = ApiClient();

  /// Upload image → AI diagnosis → returns full result
  Future<ScanResultModel> uploadScan({
    required File imageFile,
    void Function(int sent, int total)? onProgress,
  }) async {
    final data = await _api.uploadFile(
      ApiConstants.scans,
      file: imageFile,
      fieldName: 'image',
      onProgress: onProgress,
    );
    return ScanResultModel.fromJson(data);
  }

  /// Get paginated scan history
  Future<({List<ScanModel> scans, int total})> getHistory({
    int page = 1,
    int perPage = 20,
  }) async {
    final data = await _api.get(
      ApiConstants.scans,
      queryParams: {'page': page, 'per_page': perPage},
    );

    final scans = (data['scans'] as List)
        .map((s) => ScanModel.fromJson(s))
        .toList();

    return (scans: scans, total: data['total'] as int);
  }

  /// Get single scan detail
  Future<ScanModel> getScanDetail(String scanId) async {
    final data = await _api.get('${ApiConstants.scans}/$scanId');
    return ScanModel.fromJson(data['scan']);
  }
}
```

---

## 7. Disease Service

### `lib/data/repositories/disease_repository.dart`

```dart
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../models/disease_model.dart';

class DiseaseRepository {
  final _api = ApiClient();

  /// List all diseases (no auth required)
  Future<List<DiseaseModel>> getAllDiseases({
    int page = 1,
    int perPage = 50,
  }) async {
    final data = await _api.get(
      ApiConstants.diseases,
      queryParams: {'page': page, 'per_page': perPage},
    );

    return (data['diseases'] as List)
        .map((d) => DiseaseModel.fromJson(d))
        .toList();
  }

  /// Get disease detail (no auth required)
  Future<DiseaseModel> getDiseaseDetail(String diseaseId) async {
    final data = await _api.get('${ApiConstants.diseases}/$diseaseId');
    return DiseaseModel.fromJson(data['disease']);
  }
}
```

---

## 8. User Service

### `lib/data/repositories/user_repository.dart`

```dart
import '../../core/network/api_client.dart';
import '../../core/constants/api_constants.dart';
import '../models/user_model.dart';

class UserRepository {
  final _api = ApiClient();

  /// Get profile + stats
  Future<({UserModel user, UserStats stats})> getProfile() async {
    final data = await _api.get(ApiConstants.profile);
    return (
      user: UserModel.fromJson(data['user']),
      stats: UserStats.fromJson(data['stats']),
    );
  }

  /// Update display name / email
  Future<UserModel> updateProfile({
    String? displayName,
    String? email,
  }) async {
    final body = <String, dynamic>{};
    if (displayName != null) body['displayName'] = displayName;
    if (email != null) body['email'] = email;

    final data = await _api.put(ApiConstants.profile, data: body);
    return UserModel.fromJson(data['user']);
  }

  /// Change password
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await _api.put(ApiConstants.password, data: {
      'currentPassword': currentPassword,
      'newPassword': newPassword,
    });
  }
}
```

---

## 9. Screen-by-Screen Integration

### Which API for which screen?

| Screen              | API Call                      | Repository Method                        |
| ------------------- | ----------------------------- | ---------------------------------------- |
| **Splash**          | `GET /api/auth/me`            | `AuthRepository.getCurrentUser()`        |
| **Login**           | `POST /api/auth/login`        | `AuthRepository.login()`                 |
| **Register**        | `POST /api/auth/register`     | `AuthRepository.register()`              |
| **Home**            | `GET /api/scans?per_page=5`   | `ScanRepository.getHistory(perPage: 5)`  |
| **Camera/Upload**   | capture → `File`              | `ImagePicker` only (no API yet)          |
| **Processing**      | `POST /api/scans` (multipart) | `ScanRepository.uploadScan(file)`        |
| **Result**          | _(data returned from upload)_ | `ScanResultModel` from above             |
| **Disease Detail**  | `GET /api/diseases/:id`       | `DiseaseRepository.getDiseaseDetail(id)` |
| **History**         | `GET /api/scans`              | `ScanRepository.getHistory()`            |
| **History Item**    | `GET /api/scans/:id`          | `ScanRepository.getScanDetail(id)`       |
| **Profile**         | `GET /api/users/profile`      | `UserRepository.getProfile()`            |
| **Edit Profile**    | `PUT /api/users/profile`      | `UserRepository.updateProfile()`         |
| **Change Password** | `PUT /api/users/password`     | `UserRepository.changePassword()`        |

---

## 10. Error Handling & Edge Cases

### Global Error Handler

```dart
/// Wrap every API call with this
Future<T> safeApiCall<T>(Future<T> Function() call) async {
  try {
    return await call();
  } on NoInternetException {
    // Show "No internet" banner or dialog
    throw NoInternetException();
  } on ApiException catch (e) {
    if (e.statusCode == 401) {
      // Token expired → redirect to login
      await SecureStorage.clearAll();
      // Navigate to login screen
    }
    rethrow;
  }
}
```

### Edge Cases to Handle

| Scenario           | Backend Response    | Flutter Action                     |
| ------------------ | ------------------- | ---------------------------------- |
| No internet        | Connection error    | Show offline banner + retry button |
| API down           | Connection timeout  | Show "Server unavailable" + retry  |
| Token expired      | 401 Unauthorized    | Clear token → redirect to login    |
| Invalid input      | 400 + error message | Show field-specific error          |
| Duplicate email    | 409 Conflict        | Show "Email already in use"        |
| File too large     | 413                 | Show "Image too large (max 16 MB)" |
| Empty scan history | 200 + empty list    | Show empty state illustration      |
| AI model error     | 500                 | Show "Analysis failed — try again" |

### Empty State Example

```dart
Widget _buildEmptyHistory() {
  return Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.document_scanner_outlined, size: 80, color: Colors.grey[300]),
        const SizedBox(height: 16),
        Text('No scans yet', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        Text('Scan a plant to see your diagnosis history',
            style: TextStyle(color: Colors.grey[600])),
        const SizedBox(height: 24),
        ElevatedButton.icon(
          onPressed: () => Navigator.pushNamed(context, '/scan'),
          icon: const Icon(Icons.camera_alt),
          label: const Text('Scan Now'),
        ),
      ],
    ),
  );
}
```

---

## 11. State Management (Riverpod)

### `lib/data/providers/auth_provider.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_model.dart';
import '../repositories/auth_repository.dart';

// Repository provider
final authRepositoryProvider = Provider((ref) => AuthRepository());

// Auth state
enum AuthStatus { initial, authenticated, unauthenticated, loading }

class AuthState {
  final AuthStatus status;
  final UserModel? user;
  final String? error;

  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.error,
  });

  AuthState copyWith({AuthStatus? status, UserModel? user, String? error}) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      error: error,
    );
  }
}

// Auth notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repo;

  AuthNotifier(this._repo) : super(const AuthState());

  Future<void> checkAuth() async {
    try {
      final user = await _repo.getCurrentUser();
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } catch (_) {
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(status: AuthStatus.loading, error: null);
    try {
      final auth = await _repo.login(email: email, password: password);
      state = AuthState(status: AuthStatus.authenticated, user: auth.user);
    } on Exception catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
    }
  }

  Future<void> register(String name, String email, String password) async {
    state = state.copyWith(status: AuthStatus.loading, error: null);
    try {
      final auth = await _repo.register(
        displayName: name, email: email, password: password,
      );
      state = AuthState(status: AuthStatus.authenticated, user: auth.user);
    } on Exception catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        error: e.toString(),
      );
    }
  }

  Future<void> logout() async {
    await _repo.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(authRepositoryProvider));
});
```

---

## 12. Image Upload Flow

### Complete Camera → Upload → Result Flow

```dart
// 1️⃣ Pick image (camera_screen.dart)
final picker = ImagePicker();
final XFile? photo = await picker.pickImage(
  source: ImageSource.camera,  // or ImageSource.gallery
  maxWidth: 1024,
  maxHeight: 1024,
  imageQuality: 85,
);
if (photo == null) return;

// 2️⃣ Preview & confirm (preview_screen.dart)
Navigator.push(context, MaterialPageRoute(
  builder: (_) => PreviewScreen(imagePath: photo.path),
));

// 3️⃣ Upload + show processing (processing_screen.dart)
final file = File(photo.path);
final result = await ScanRepository().uploadScan(
  imageFile: file,
  onProgress: (sent, total) {
    // Update progress bar: sent / total
    setState(() => _progress = sent / total);
  },
);

// 4️⃣ Show result (result_screen.dart)
Navigator.pushReplacement(context, MaterialPageRoute(
  builder: (_) => ResultScreen(result: result),
));
```

### Result Screen Data Mapping

```dart
class ResultScreen extends StatelessWidget {
  final ScanResultModel result;
  const ResultScreen({required this.result});

  @override
  Widget build(BuildContext context) {
    final pred = result.prediction;
    final disease = result.disease;

    return Scaffold(
      body: Column(
        children: [
          // Scanned image
          Image.network(result.scan.imageUrl),

          // Disease name
          Text(pred.diseaseName),        // "Late blight"

          // Confidence
          Text(pred.confidencePercent),  // "97.2%"

          // Healthy badge
          if (pred.isHealthy)
            const Chip(label: Text('Healthy ✅')),

          // View details button
          if (disease != null)
            ElevatedButton(
              onPressed: () => Navigator.push(context, MaterialPageRoute(
                builder: (_) => DiseaseDetailScreen(disease: disease),
              )),
              child: const Text('View Details'),
            ),

          // Save result — already saved in DB automatically!
          // Just show a confirmation message.
        ],
      ),
    );
  }
}
```

---

## Base URL Quick Reference

| Environment                 | `base_url` value           |
| --------------------------- | -------------------------- |
| Android Emulator            | `http://10.0.2.2:5000`     |
| iOS Simulator               | `http://127.0.0.1:5000`    |
| Physical Device (same WiFi) | `http://<YOUR_PC_IP>:5000` |
| Production                  | `https://your-domain.com`  |

> **Tip:** Find your PC IP with `ipconfig` (Windows) or `ifconfig` (macOS/Linux).
> The server is already configured with `host="0.0.0.0"` so it accepts connections from any device on your network.

---

## Response Format Reference

Every API response follows this pattern:

```
✅ Success:  { "data_key": { ... } }           → 200/201
❌ Error:    { "error": "Human-readable message" } → 400/401/403/404/409/500
```

Your Dio interceptor extracts the `error` field automatically — just catch `ApiException` and show `e.message` to the user.
