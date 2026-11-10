"""Testes exclusivamente sintéticos. Não acessam Kubernetes ou rede."""
import json
import subprocess
import unittest
from types import SimpleNamespace
from dashboard import Kubernetes, error_message, pod_row, service_rows, snapshot, valid_namespace


class DashboardTests(unittest.TestCase):
    def test_context_pinned_and_only_get(self):
        calls = []
        def run(args, **kwargs):
            calls.append(args)
            self.assertFalse(kwargs['shell'])
            return SimpleNamespace(returncode=0, stderr='', stdout='lab\n' if len(calls)==1 else '{"items":[]}')
        client = Kubernetes(run)
        client.get('pods', 'nyx-stg')
        self.assertEqual(calls[0], ['kubectl','config','current-context'])
        self.assertIn('lab', calls[1])
        self.assertIn('get', calls[1])
        with self.assertRaises(ValueError): client.get('secrets', 'default')
        with self.assertRaises(ValueError): client.get('pods', '--all-namespaces')
        self.assertEqual(len(calls), 2)

    def test_namespace(self):
        for value in ('default', 'a', 'nyx-stg'): self.assertTrue(valid_namespace(value))
        for value in ('', 'A', 'a b', '-a', 'a-', 'x'*64, 'x;id'): self.assertFalse(valid_namespace(value))

    def test_missing_kubectl(self):
        def run(*args, **kwargs): raise FileNotFoundError()
        client = Kubernetes(run)
        self.assertIn('não encontrado', client.start_error)
        with self.assertRaises(RuntimeError): client.get('pods','default')

    def test_timeout_and_redaction(self):
        def run(*args, **kwargs): raise subprocess.TimeoutExpired('sensitive', 15)
        client = Kubernetes(run)
        self.assertNotIn('sensitive', client.start_error)
        self.assertIn('15 segundos', client.start_error)
        self.assertNotIn('SECRET', error_message('Unauthorized SECRET'))
        self.assertIn('Permissão', error_message('Forbidden SECRET'))

    def test_pod_failure_and_init_restarts(self):
        row = pod_row({'metadata':{'name':'nyx'},'status':{'phase':'Running',
           'initContainerStatuses':[{'restartCount':2}], 'containerStatuses':[{
           'restartCount':17, 'state':{'waiting':{'reason':'CrashLoopBackOff'}},
           'lastState':{'terminated':{'reason':'OOMKilled'}}}]}})
        self.assertEqual(row['reinicios'],19)
        self.assertIn('OOMKilled',row['motivo'])
        self.assertIn('CrashLoopBackOff',row['motivo'])
        self.assertFalse(row['pronto'])

    def test_pod_missing_optional_fields(self):
        row=pod_row({})
        self.assertEqual(row['reinicios'],0)
        self.assertEqual(row['fase'],'Desconhecida')

    def test_endpoints_missing_unknown_and_external(self):
        svc=[{'metadata':{'name':'nyx'}}]
        self.assertEqual(service_rows(svc,[])[0]['endpoints'],'Sem endpoint pronto')
        self.assertIn('Desconhecido',service_rows(svc,None)[0]['endpoints'])
        self.assertIn('DNS externo',service_rows([{'spec':{'type':'ExternalName'}}],[])[0]['endpoints'])

    def test_slices_aggregate_deduplicate(self):
        item={'metadata':{'labels':{'kubernetes.io/service-name':'nyx'}},'endpoints':[
            {'addresses':['10.0.0.1'],'conditions':{'ready':True}},
            {'addresses':['10.0.0.2'],'conditions':{'ready':False}},
            {'addresses':['10.0.0.3']}]}
        row=service_rows([{'metadata':{'name':'nyx'}}],[item,item])[0]
        self.assertEqual(row['endpoints'],'1 endereço(s) pronto(s); 1 com prontidão desconhecida')

    def test_partial_failure_and_zero_ready(self):
        class Client:
            context='lab'
            def get(self, resource, namespace):
                if resource=='endpointslices.discovery.k8s.io': raise RuntimeError('Permissão negada.')
                if resource=='deployments': return [{'metadata':{'name':'orion'},'spec':{'replicas':3}}]
                if resource=='services': return [{'metadata':{'name':'orion'}}]
                return []
        result=snapshot(Client(),'default')
        self.assertEqual(result['deployments'][0]['prontos'],0)
        self.assertEqual(result['deployments'][0]['desejados'],3)
        self.assertIn('Desconhecido',result['services'][0]['endpoints'])
        self.assertEqual(len(result['erros']),1)

    def test_invalid_json(self):
        calls=[]
        def run(*args, **kwargs):
            calls.append(1)
            return SimpleNamespace(returncode=0,stderr='',stdout='lab' if len(calls)==1 else '{}')
        with self.assertRaisesRegex(RuntimeError,'JSON inválida'): Kubernetes(run).get('pods','default')


if __name__=='__main__': unittest.main()
