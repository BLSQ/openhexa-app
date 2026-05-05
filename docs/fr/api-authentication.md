<div class="hero-section">
  <h1><i class="fas fa-hexagon" style="margin-right: 0.5rem;"></i>Authentification API</h1>
</div>
</div>

OpenHEXA fournit une authentification basée sur JWT pour l'accès programmatique aux espaces de travail et à leurs ressources. Cela permet aux applications et services externes de s'authentifier et d'interagir avec les espaces de travail OpenHEXA en toute sécurité.

## Génération de jetons JWT

### Vue d'ensemble

OpenHEXA peut émettre des jetons JWT (JSON Web Token) pour l'accès aux espaces de travail. Ces jetons contiennent des informations d'appartenance à l'espace de travail et des claims d'identité utilisateur, permettant aux services externes d'authentifier les requêtes API.

### Émettre un jeton d'espace de travail

Pour émettre un jeton JWT pour un espace de travail, utilisez la mutation GraphQL `issueWorkspaceToken` :

```graphql
mutation IssueWorkspaceToken($input: IssueWorkspaceTokenInput!) {
  issueWorkspaceToken(input: $input) {
    success
    token
    expiresAt
    workspace {
      id
      slug
    }
    role
    errors
  }
}
```

**Paramètres d'entrée :**

Vous devez fournir exactement l'un des éléments suivants :
- `workspaceId` (UUID) - L'identifiant unique de l'espace de travail
- `workspaceSlug` (String) - Le slug de l'espace de travail

**Exemple :**

```graphql
{
  "input": {
    "workspaceSlug": "my-workspace"
  }
}
```

**Réponse :**

```json
{
  "success": true,
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im9wdGlvbmFsLWtleS1pZCJ9...",
  "expiresAt": "2025-11-06T12:30:00Z",
  "workspace": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "slug": "my-workspace"
  },
  "role": "EDITOR",
  "errors": []
}
```

### Charge utile du jeton

Le jeton JWT généré contient les claims suivants :

- **Claims standard :**
  - `sub` - Sujet (ID utilisateur)
  - `iss` - Émetteur (par défaut : https://app.openhexa.org)
  - `aud` - Audience (par défaut : openhexa-clients)
  - `iat` - Horodatage d'émission
  - `exp` - Horodatage d'expiration
  - `jti` - ID JWT (identifiant unique du jeton)

- **Claims personnalisés :**
  - `https://app.openhexa.org/claims/workspace` - Informations sur l'espace de travail (id, slug)
  - `https://app.openhexa.org/claims/workspace_role` - Rôle de l'utilisateur dans l'espace de travail (OWNER, ADMIN, EDITOR, VIEWER)
  - `https://app.openhexa.org/claims/user` - Informations sur l'utilisateur (id, email)

### Gestion des erreurs

La mutation peut renvoyer les erreurs suivantes :

- `AUTH_UNAUTHENTICATED` - L'utilisateur n'est pas authentifié
- `INPUT_INVALID` - workspaceId et workspaceSlug ont tous deux été fournis ou aucun
- `WORKSPACE_NOT_FOUND` - L'espace de travail n'existe pas
- `MEMBERSHIP_REQUIRED` - L'utilisateur n'est pas membre de l'espace de travail
- `CONFIG_MISSING_PRIVATE_KEY` - La clé privée JWT n'est pas configurée sur le serveur
- `ROLE_UNRESOLVED` - Le rôle de l'utilisateur dans l'espace de travail n'a pas pu être déterminé
- `CLOCK_ERROR` - Erreur d'horloge système

## Vérification des jetons

### Point de terminaison JWKS

OpenHEXA expose un point de terminaison JSON Web Key Set (JWKS) pour la vérification des jetons à :

```
GET /.well-known/jwks.json
```

Ce point de terminaison renvoie la ou les clés publiques utilisées pour vérifier les jetons JWT émis par OpenHEXA.

**Exemple de réponse :**

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "kid": "optional-key-id",
      "n": "base64url-encoded-modulus",
      "e": "base64url-encoded-exponent"
    }
  ]
}
```

### Vérifier les jetons

Les services externes peuvent vérifier les jetons JWT OpenHEXA à l'aide de la clé publique du point de terminaison JWKS. La plupart des bibliothèques JWT prennent en charge la vérification basée sur JWKS.

**Exemple en Python :**

```python
import jwt
from jwt import PyJWKClient

# Récupérer la clé publique depuis le point de terminaison JWKS
jwks_client = PyJWKClient("https://your-openhexa-instance/.well-known/jwks.json")
signing_key = jwks_client.get_signing_key_from_jwt(token)

# Vérifier le jeton
decoded = jwt.decode(
    token,
    signing_key.key,
    algorithms=["RS256"],
    audience="openhexa-clients",
    issuer="https://app.openhexa.org"
)

# Accéder aux claims
workspace_id = decoded["https://app.openhexa.org/claims/workspace"]["id"]
user_role = decoded["https://app.openhexa.org/claims/workspace_role"]
```

## Configuration

### Configuration du serveur

Pour activer la génération de jetons JWT, configurez les variables d'environnement suivantes sur le serveur OpenHEXA :

- `OPENHEXA_JWT_PRIVATE_KEY` (requis) - Clé privée RSA au format PEM
- `OPENHEXA_JWT_KID` (optionnel) - Identifiant de clé à inclure dans les en-têtes des jetons
- `OPENHEXA_JWT_ISSUER` (optionnel) - Émetteur du jeton, par défaut `https://app.openhexa.org`
- `OPENHEXA_JWT_AUDIENCE` (optionnel) - Audience du jeton, par défaut `openhexa-clients`
- `OPENHEXA_JWT_TTL` (optionnel) - Durée de vie du jeton en secondes, par défaut `3600` (1 heure)

**Exemple de configuration `.env` :**

```bash
OPENHEXA_JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----"
OPENHEXA_JWT_KID=my-key-identifier
OPENHEXA_JWT_TTL=7200
```

### Génération d'une paire de clés RSA

Vous pouvez générer une paire de clés RSA avec OpenSSL :

```bash
# Générer la clé privée
openssl genrsa -out private_key.pem 2048

# Extraire la clé publique
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

## Considérations de sécurité

- **Stockage des jetons :** Stockez les jetons JWT en lieu sûr et ne les exposez jamais dans le code côté client ni dans les journaux
- **Expiration des jetons :** Les jetons expirent après le TTL configuré (par défaut 1 heure). Demandez de nouveaux jetons selon les besoins
- **HTTPS uniquement :** Utilisez toujours HTTPS lors de la transmission des jetons JWT
- **Rotation des clés :** Effectuez régulièrement la rotation des paires de clés RSA et mettez à jour la configuration du serveur
- **Limitation de portée :** Les jetons sont limités à un espace de travail spécifique et à l'appartenance d'un utilisateur
- **Contrôle d'accès basé sur les rôles :** Les claims du jeton incluent le rôle de l'utilisateur, qui doit être appliqué par les applications consommatrices

## Cas d'usage

Les jetons JWT sont utiles pour :

- **Intégration API :** Authentifier les applications externes accédant à l'API GraphQL d'OpenHEXA
- **Communication service-à-service :** Permettre la communication sécurisée entre microservices
- **Outils tiers :** Intégrer OpenHEXA avec des outils d'analyse ou de monitoring externes
- **Clients personnalisés :** Construire des applications personnalisées qui interagissent avec les espaces de travail OpenHEXA
- **Workflows automatisés :** Authentifier les scripts automatisés et les pipelines de données s'exécutant en dehors d'OpenHEXA
