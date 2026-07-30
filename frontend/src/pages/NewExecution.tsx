import React, { useState } from 'react';
import { apiClient as api } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { GlassPanel } from '../components/ui/GlassPanel';
import { PageHeader } from '../components/layout/PageHeader';
import { Breadcrumb } from '../components/layout/Breadcrumb';

type FormState = 'IDLE' | 'LOADING' | 'PROCESSANDO' | 'CONCLUIDO' | 'ERRO';

export const NewExecution: React.FC = () => {
  const [despesas, setDespesas] = useState<File | null>(null);
  const [razao, setRazao] = useState<File | null>(null);
  const [extrato, setExtrato] = useState<File | null>(null);
  
  const [status, setStatus] = useState<FormState>('IDLE');
  const [errorMsg, setErrorMsg] = useState('');
  
  const navigate = useNavigate();

  const handleFileChange = (setter: React.Dispatch<React.SetStateAction<File | null>>) => (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setter(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!despesas || !razao || !extrato) {
      setErrorMsg('Por favor, selecione os três arquivos.');
      return;
    }

    try {
      setStatus('LOADING');
      setErrorMsg('');

      // 1. Create Execution
      const res = await api.post('/executions');
      const execution = res.data;

      // 2. Upload Files
      const formData = new FormData();
      formData.append('despesas', despesas);
      formData.append('razao', razao);
      formData.append('extrato', extrato);
      await api.post(`/executions/${execution.id}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // 3. Start Run
      setStatus('PROCESSANDO');
      await api.post(`/executions/${execution.id}/run`);
      
      setStatus('CONCLUIDO');
      
      setTimeout(() => navigate(`/executions/${execution.id}`), 1500);
      
    } catch (err: any) {
      console.error(err);
      setStatus('ERRO');
      setErrorMsg('Ocorreu um erro durante a criação da execução.');
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <Breadcrumb items={[{ label: 'Execuções', href: '/executions' }, { label: 'Nova Conciliação' }]} />
      <PageHeader title="Nova Conciliação" description="Inicie um novo processo de conciliação enviando os arquivos base." />

      <GlassPanel className="p-8">
        {status === 'ERRO' && (
          <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg mb-6">
            {errorMsg}
          </div>
        )}
        
        {status === 'CONCLUIDO' && (
          <div className="p-4 bg-green-50 text-green-700 border border-green-200 rounded-lg mb-6">
            Pipeline iniciada com sucesso! Redirecionando...
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">Arquivo de Despesas (XLSX/CSV)</label>
            <input type="file" accept=".xlsx,.csv" onChange={handleFileChange(setDespesas)} disabled={status !== 'IDLE' && status !== 'ERRO'} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
            {despesas && <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Selecionado: {despesas.name}</p>}
          </div>

          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">Arquivo de Razão (XLSX/CSV)</label>
            <input type="file" accept=".xlsx,.csv" onChange={handleFileChange(setRazao)} disabled={status !== 'IDLE' && status !== 'ERRO'} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
            {razao && <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Selecionado: {razao.name}</p>}
          </div>

          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">Arquivo de Extrato (XLSX/CSV)</label>
            <input type="file" accept=".xlsx,.csv" onChange={handleFileChange(setExtrato)} disabled={status !== 'IDLE' && status !== 'ERRO'} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
            {extrato && <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Selecionado: {extrato.name}</p>}
          </div>

          <div className="pt-4 flex justify-end">
            <Button 
              type="submit" 
              isLoading={status === 'LOADING' || status === 'PROCESSANDO' || status === 'CONCLUIDO'}
            >
              {status === 'IDLE' && 'Iniciar Conciliação'}
              {status === 'LOADING' && 'Enviando Arquivos...'}
              {status === 'PROCESSANDO' && 'Iniciando Pipeline...'}
              {status === 'CONCLUIDO' && 'Concluído'}
              {status === 'ERRO' && 'Tentar Novamente'}
            </Button>
          </div>
        </form>
      </GlassPanel>
    </div>
  );
};
