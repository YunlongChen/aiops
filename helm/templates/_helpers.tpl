{{/*
AIOps-Platform Helm Chart辅助模板
文件: _helpers.tpl
描述: 定义通用的标签、选择器和命名函数
版本: 1.0.0
作者: AIOps Team
*/}}

{{/*
展开chart的名称
*/}}
{{- define "aiops.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
创建一个默认的完全限定应用名称
我们截断到63个字符，因为某些Kubernetes名称字段受此限制（由DNS命名规范）
如果发布名称包含chart名称，它将被用作完整名称
*/}}
{{- define "aiops.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
创建chart名称和版本，用作chart标签
*/}}
{{- define "aiops.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
通用标签
*/}}
{{- define "aiops.labels" -}}
helm.sh/chart: {{ include "aiops.chart" . }}
{{ include "aiops.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.global.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
选择器标签
*/}}
{{- define "aiops.selectorLabels" -}}
app.kubernetes.io/name: {{ include "aiops.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
创建服务账户的名称
*/}}
{{- define "aiops.serviceAccountName" -}}
{{- if .Values.global.serviceAccount.create }}
{{- default (include "aiops.fullname" .) .Values.global.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.global.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
创建命名空间名称
*/}}
{{- define "aiops.namespace" -}}
{{- default .Release.Namespace .Values.namespaceOverride }}
{{- end }}

{{/*
创建镜像拉取策略
*/}}
{{- define "aiops.imagePullPolicy" -}}
{{- default "IfNotPresent" .pullPolicy }}
{{- end }}

{{/*
创建镜像仓库URL
*/}}
{{- define "aiops.imageRegistry" -}}
{{- if .Values.global.imageRegistry }}
{{- printf "%s/" .Values.global.imageRegistry }}
{{- end }}
{{- end }}

{{/*
创建完整的镜像名称
*/}}
{{- define "aiops.image" -}}
{{- $registry := include "aiops.imageRegistry" . }}
{{- printf "%s%s:%s" $registry .repository .tag }}
{{- end }}

{{/*
创建存储类名称
*/}}
{{- define "aiops.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else if .storageClass }}
{{- .storageClass }}
{{- else }}
{{- "" }}
{{- end }}
{{- end }}

{{/*
创建PVC名称
*/}}
{{- define "aiops.pvcName" -}}
{{- printf "%s-%s" (include "aiops.fullname" .) .suffix }}
{{- end }}

{{/*
创建ConfigMap名称
*/}}
{{- define "aiops.configMapName" -}}
{{- printf "%s-%s" (include "aiops.fullname" .) .suffix }}
{{- end }}

{{/*
创建Secret名称
*/}}
{{- define "aiops.secretName" -}}
{{- printf "%s-%s" (include "aiops.fullname" .) .suffix }}
{{- end }}

{{/*
创建Ingress主机名
*/}}
{{- define "aiops.ingressHost" -}}
{{- if .host }}
{{- .host }}
{{- else }}
{{- printf "%s.%s" (include "aiops.fullname" .) .Values.global.clusterDomain }}
{{- end }}
{{- end }}

{{/*
创建资源限制
*/}}
{{- define "aiops.resources" -}}
{{- if .resources }}
resources:
  {{- if .resources.limits }}
  limits:
    {{- if .resources.limits.cpu }}
    cpu: {{ .resources.limits.cpu }}
    {{- end }}
    {{- if .resources.limits.memory }}
    memory: {{ .resources.limits.memory }}
    {{- end }}
  {{- end }}
  {{- if .resources.requests }}
  requests:
    {{- if .resources.requests.cpu }}
    cpu: {{ .resources.requests.cpu }}
    {{- end }}
    {{- if .resources.requests.memory }}
    memory: {{ .resources.requests.memory }}
    {{- end }}
  {{- end }}
{{- end }}
{{- end }}

{{/*
创建节点选择器
*/}}
{{- define "aiops.nodeSelector" -}}
{{- if .nodeSelector }}
nodeSelector:
  {{- toYaml .nodeSelector | nindent 2 }}
{{- end }}
{{- end }}

{{/*
创建容忍度
*/}}
{{- define "aiops.tolerations" -}}
{{- if .tolerations }}
tolerations:
  {{- toYaml .tolerations | nindent 2 }}
{{- end }}
{{- end }}

{{/*
创建亲和性
*/}}
{{- define "aiops.affinity" -}}
{{- if .affinity }}
affinity:
  {{- toYaml .affinity | nindent 2 }}
{{- end }}
{{- end }}

{{/*
创建安全上下文
*/}}
{{- define "aiops.securityContext" -}}
{{- if .Values.global.securityContext }}
securityContext:
  {{- toYaml .Values.global.securityContext | nindent 2 }}
{{- end }}
{{- end }}

{{/*
创建Pod安全上下文
*/}}
{{- define "aiops.podSecurityContext" -}}
{{- if .podSecurityContext }}
securityContext:
  {{- toYaml .podSecurityContext | nindent 2 }}
{{- else if .Values.global.securityContext }}
securityContext:
  {{- toYaml .Values.global.securityContext | nindent 2 }}
{{- end }}
{{- end }}

{{/*
创建环境变量
*/}}
{{- define "aiops.env" -}}
{{- if .env }}
env:
{{- range .env }}
  - name: {{ .name }}
    {{- if .value }}
    value: {{ .value | quote }}
    {{- else if .valueFrom }}
    valueFrom:
      {{- toYaml .valueFrom | nindent 6 }}
    {{- end }}
{{- end }}
{{- end }}
{{- end }}

{{/*
创建卷挂载
*/}}
{{- define "aiops.volumeMounts" -}}
{{- if .volumeMounts }}
volumeMounts:
{{- range .volumeMounts }}
  - name: {{ .name }}
    mountPath: {{ .mountPath }}
    {{- if .subPath }}
    subPath: {{ .subPath }}
    {{- end }}
    {{- if .readOnly }}
    readOnly: {{ .readOnly }}
    {{- end }}
{{- end }}
{{- end }}
{{- end }}

{{/*
创建卷
*/}}
{{- define "aiops.volumes" -}}
{{- if .volumes }}
volumes:
{{- range .volumes }}
  - name: {{ .name }}
    {{- if .configMap }}
    configMap:
      name: {{ .configMap.name }}
      {{- if .configMap.items }}
      items:
        {{- toYaml .configMap.items | nindent 8 }}
      {{- end }}
    {{- else if .secret }}
    secret:
      secretName: {{ .secret.secretName }}
      {{- if .secret.items }}
      items:
        {{- toYaml .secret.items | nindent 8 }}
      {{- end }}
    {{- else if .persistentVolumeClaim }}
    persistentVolumeClaim:
      claimName: {{ .persistentVolumeClaim.claimName }}
    {{- else if .emptyDir }}
    emptyDir: {}
    {{- else if .hostPath }}
    hostPath:
      path: {{ .hostPath.path }}
      {{- if .hostPath.type }}
      type: {{ .hostPath.type }}
      {{- end }}
    {{- end }}
{{- end }}
{{- end }}
{{- end }}

{{/*
创建探针配置
*/}}
{{- define "aiops.probe" -}}
{{- if .httpGet }}
httpGet:
  path: {{ .httpGet.path }}
  port: {{ .httpGet.port }}
  {{- if .httpGet.scheme }}
  scheme: {{ .httpGet.scheme }}
  {{- end }}
{{- else if .tcpSocket }}
tcpSocket:
  port: {{ .tcpSocket.port }}
{{- else if .exec }}
exec:
  command:
    {{- toYaml .exec.command | nindent 4 }}
{{- end }}
{{- if .initialDelaySeconds }}
initialDelaySeconds: {{ .initialDelaySeconds }}
{{- end }}
{{- if .periodSeconds }}
periodSeconds: {{ .periodSeconds }}
{{- end }}
{{- if .timeoutSeconds }}
timeoutSeconds: {{ .timeoutSeconds }}
{{- end }}
{{- if .successThreshold }}
successThreshold: {{ .successThreshold }}
{{- end }}
{{- if .failureThreshold }}
failureThreshold: {{ .failureThreshold }}
{{- end }}
{{- end }}

{{/*
创建HPA配置
*/}}
{{- define "aiops.hpa" -}}
{{- if .autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "aiops.fullname" . }}-{{ .component }}
  labels:
    {{- include "aiops.labels" . | nindent 4 }}
    app.kubernetes.io/component: {{ .component }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "aiops.fullname" . }}-{{ .component }}
  minReplicas: {{ .autoscaling.minReplicas }}
  maxReplicas: {{ .autoscaling.maxReplicas }}
  metrics:
    {{- if .autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
{{- end }}
{{- end }}

{{/*
创建网络策略
*/}}
{{- define "aiops.networkPolicy" -}}
{{- if .Values.networkPolicy.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "aiops.fullname" . }}-{{ .component }}
  labels:
    {{- include "aiops.labels" . | nindent 4 }}
    app.kubernetes.io/component: {{ .component }}
spec:
  podSelector:
    matchLabels:
      {{- include "aiops.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: {{ .component }}
  policyTypes:
    - Ingress
    - Egress
  {{- if .Values.networkPolicy.ingress }}
  ingress:
    {{- toYaml .Values.networkPolicy.ingress | nindent 4 }}
  {{- end }}
  {{- if .Values.networkPolicy.egress }}
  egress:
    {{- toYaml .Values.networkPolicy.egress | nindent 4 }}
  {{- end }}
{{- end }}
{{- end }}

{{/*
创建ServiceMonitor
*/}}
{{- define "aiops.serviceMonitor" -}}
{{- if .Values.monitoring.serviceMonitor.enabled }}
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ include "aiops.fullname" . }}-{{ .component }}
  {{- if .Values.monitoring.serviceMonitor.namespace }}
  namespace: {{ .Values.monitoring.serviceMonitor.namespace }}
  {{- end }}
  labels:
    {{- include "aiops.labels" . | nindent 4 }}
    app.kubernetes.io/component: {{ .component }}
    {{- with .Values.monitoring.serviceMonitor.labels }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
spec:
  selector:
    matchLabels:
      {{- include "aiops.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: {{ .component }}
  endpoints:
    - port: http
      {{- if .Values.monitoring.serviceMonitor.interval }}
      interval: {{ .Values.monitoring.serviceMonitor.interval }}
      {{- end }}
      {{- if .Values.monitoring.serviceMonitor.scrapeTimeout }}
      scrapeTimeout: {{ .Values.monitoring.serviceMonitor.scrapeTimeout }}
      {{- end }}
      path: /metrics
{{- end }}
{{- end }}