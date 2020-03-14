{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "panopticum.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "panopticum.fullname" -}}
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

{{/*
Return the proper Panopticum image name
*/}}
{{- define "panopticum.image" -}}
{{- $registryName := .Values.image.registry -}}
{{- $repositoryName := .Values.image.repository -}}
{{- $tag := .Values.image.tag | toString -}}
{{/*
Helm 2.11 supports the assignment of a value to a variable defined in a different scope,
but Helm 2.9 and 2.10 doesn't support it, so we need to implement this if-else logic.
Also, we can't use a single if because lazy evaluation is not an option
*/}}

{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}

{{- end -}}

{{/*
Return the proper Panopticum image name
*/}}
{{- define "panopticum.configsFromImage-image" -}}
{{- $registryName := .Values.configsFromImage.image.registry -}}
{{- $repositoryName := .Values.configsFromImage.image.repository -}}
{{- $tag := .Values.configsFromImage.image.tag | toString -}}

{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}

{{- end -}}

{{/*
Return the proper Panopticum fixtures image name
*/}}
{{- define "panopticum.fixtures.image" -}}
{{- $registryName := .Values.fixtures.image.registry -}}
{{- $repositoryName := .Values.fixtures.image.repository -}}
{{- $tag := .Values.fixtures.image.tag | toString -}}

{{- printf "%s/%s:%s" $registryName $repositoryName $tag -}}

{{- end -}}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "panopticum.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "panopticum.dbvars" -}}
- name: APP_DB_ENGINE
  value: {{ .Values.database.engine }}
- name: DB_HOST
  value: {{ .Values.database.host }}
- name: DB_PORT
  value: {{ .Values.database.port | quote }}
- name: DB_NAME
  value: {{ .Values.database.name | quote }}
- name: DB_USER
  value: {{ .Values.database.user | quote }}
- name: DB_PASSWORD
  value: {{ .Values.database.password | quote }}
{{- end -}}