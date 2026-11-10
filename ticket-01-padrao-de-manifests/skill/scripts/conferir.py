"""Conferência estática parcial. Nunca acessa o cluster nem imprime valores secretos."""
import argparse
import json
import re
import sys
from pathlib import Path
import yaml

NOME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NAMESPACE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*-(dev|stg|prod)")
LABELS = ("name", "instance", "part-of", "managed-by")


def conferir(objetos):
    achados = []
    def erro(obj, regra, mensagem):
        meta = obj.get("metadata") or {}
        achados.append({"objeto": str(meta.get("name", "sem-nome")), "regra": regra, "mensagem": mensagem})
    workloads = []
    for obj in objetos:
        if not isinstance(obj, dict) or not isinstance(obj.get("metadata"), dict):
            raise ValueError("Documento sem metadata válida")
        meta = obj["metadata"]
        nome = meta.get("name", "")
        ns = meta.get("namespace", "")
        if not isinstance(nome, str) or not NOME.fullmatch(nome):
            erro(obj, "1.1", "Nome fora de kebab-case")
        # Namespace é objeto de escopo global; seu próprio nome carrega o padrão.
        alvo_ns = nome if obj.get("kind") == "Namespace" else ns
        if not isinstance(alvo_ns, str) or not NAMESPACE.fullmatch(alvo_ns):
            erro(obj, "1.2", "Namespace fora do formato cliente-ambiente; escopo global não suportado exige revisão")
        labels = meta.get("labels") or {}
        for label in LABELS:
            if not labels.get("app.kubernetes.io/" + label):
                erro(obj, "1.3", "Label obrigatória ausente: " + label)
        if labels.get("app.kubernetes.io/managed-by") not in {"platform", "argocd", "helm"}:
            erro(obj, "1.3", "managed-by fora dos valores permitidos")
        if alvo_ns and labels.get("app.kubernetes.io/instance") != alvo_ns:
            erro(obj, "1.3", "instance não corresponde à instalação")
        if isinstance(alvo_ns, str) and labels.get("app.kubernetes.io/part-of") != alvo_ns.rsplit("-", 1)[0]:
            erro(obj, "1.3", "part-of não corresponde ao cliente")
        spec = obj.get("spec") or {}
        if obj.get("kind") in {"Deployment", "StatefulSet", "DaemonSet", "Job"}:
            template = spec.get("template") or {}
            pod = template.get("spec") or {}
            podlabels = (template.get("metadata") or {}).get("labels") or {}
            workloads.append((ns, podlabels))
            selector = spec.get("selector") or {}
            if selector.get("matchExpressions"):
                erro(obj, "1.4", "matchExpressions exige revisão; não coberto pelo script")
            match = selector.get("matchLabels") or {}
            if obj.get("kind") != "Job" and (not match or any(podlabels.get(k) != v for k, v in match.items())):
                erro(obj, "1.4", "matchLabels não corresponde aos rótulos do pod")
            if str(ns).endswith("-prod") and obj.get("kind") == "Deployment":
                replicas = spec.get("replicas", 1)
                if not isinstance(replicas, int) or isinstance(replicas, bool) or replicas < 2:
                    erro(obj, "2.3", "Produção exige ao menos duas réplicas")
                strategy = spec.get("strategy") or {}
                rolling = strategy.get("rollingUpdate") or {}
                if strategy.get("type") != "RollingUpdate" or rolling.get("maxUnavailable") != 0 or rolling.get("maxSurge") != 1:
                    erro(obj, "2.4", "Produção exige RollingUpdate com maxUnavailable 0 e maxSurge 1")
            for container in (pod.get("containers") or []) + (pod.get("initContainers") or []):
                image = container.get("image", "")
                final = image.rsplit("/", 1)[-1]
                if "@sha256:" not in image and (":" not in final or final.endswith(":latest")):
                    erro(obj, "3.1", "Imagem sem versão explícita ou com latest")
                if not image.startswith("registry.metacortex.io/"):
                    erro(obj, "3.7", "Imagem fora do registry interno")
                for env in container.get("env") or []:
                    if "value" in env and re.search(r"PASSWORD|TOKEN|SECRET|PRIVATE_KEY|DATABASE_URL", str(env.get("name", "")), re.I):
                        erro(obj, "3.3", "Variável potencialmente sensível usa valor direto; usar secretKeyRef")
        elif obj.get("kind") == "Secret" and (obj.get("data") or obj.get("stringData")):
            erro(obj, "3.3", "Secret preenchido não deve ser versionado")
        elif obj.get("kind") not in {"Service", "ConfigMap", "ServiceAccount", "Namespace", "PodDisruptionBudget", "Secret"}:
            erro(obj, "escopo", "Tipo não coberto pelo verificador; revisar manualmente")
    for obj in objetos:
        if obj.get("kind") == "Service":
            spec = obj.get("spec") or {}
            selector = spec.get("selector") or {}
            ns = obj["metadata"].get("namespace")
            if not selector or not any(ns == wns and all(labels.get(k) == v for k, v in selector.items()) for wns, labels in workloads):
                erro(obj, "1.4", "Nenhum template fornecido corresponde ao Service; destino externo não verificado")
    return achados


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivos", nargs="+")
    args = parser.parse_args()
    try:
        objetos = []
        for nome in args.arquivos:
            texto = Path(nome).read_text(encoding="utf-8-sig")
            objetos.extend(x for x in yaml.safe_load_all(texto) if x is not None)
        if not objetos:
            raise ValueError("Nenhum objeto")
        achados = conferir(objetos)
    except (OSError, ValueError, yaml.YAMLError, TypeError, AttributeError):
        print("Entrada inválida ou inacessível; confira o YAML. Conteúdo omitido para proteger segredos.", file=sys.stderr)
        return 2
    print(json.dumps({"escopo": "verificação estática parcial; não equivale a conformidade integral", "achados": achados}, ensure_ascii=False, indent=2))
    return 1 if achados else 0


if __name__ == "__main__":
    raise SystemExit(main())
