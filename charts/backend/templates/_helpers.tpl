{{- define "dialog-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "dialog-backend.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "dialog-backend.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/name: {{ include "dialog-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "dialog-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dialog-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Fully-qualified container image reference for the backend image.
One image backs all three roles (api / worker / gateway); the role is
selected by the container command in each Deployment.
*/}}
{{- define "dialog-backend.image" -}}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) -}}
{{- end -}}

{{/*
Redis connection URL. When the in-cluster Redis is enabled, build the URL
from its Service; otherwise fall back to the externally-provided redis.url.
*/}}
{{- define "dialog-backend.redisUrl" -}}
{{- if .Values.redis.enabled -}}
{{- printf "redis://%s-redis:6379/0" (include "dialog-backend.fullname" .) -}}
{{- else -}}
{{- .Values.redis.url -}}
{{- end -}}
{{- end -}}

{{/*
Name of the Secret holding MinIO/S3 root credentials (keys: root-user,
root-password). Prefers an existing Secret when provided.
*/}}
{{- define "dialog-backend.minioSecretName" -}}
{{- .Values.minio.existingSecret | default (printf "%s-minio" (include "dialog-backend.fullname" .)) -}}
{{- end -}}

{{/*
Name of the Secret holding LLM credentials (keys: ollama-api-key,
azure-openai-api-key). Prefers an existing Secret when provided.
*/}}
{{- define "dialog-backend.llmSecretName" -}}
{{- .Values.llm.existingSecret | default (printf "%s-llm" (include "dialog-backend.fullname" .)) -}}
{{- end -}}

{{/*
S3 endpoint URL. Uses the in-cluster MinIO Service when enabled, otherwise
the externally-provided endpoint.
*/}}
{{- define "dialog-backend.s3EndpointUrl" -}}
{{- if .Values.minio.enabled -}}
{{- printf "http://%s-minio:9000" (include "dialog-backend.fullname" .) -}}
{{- else -}}
{{- .Values.minio.endpointUrl -}}
{{- end -}}
{{- end -}}
