import React, { useState } from 'react';
import { apiClient as api } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { GlassPanel } from '../components/ui/GlassPanel';
import { PageHeader } from '../components/layout/PageHeader';
import { Breadcrumb } from '../components/layout/Breadcrumb';
import { FileUp, FileSpreadsheet, AlertCircle, CheckCircle2 } from 'lucide-react';

type FormState = 'IDLE' | 'LOADING' | 'PROCESSANDO' | 'CONCLUIDO' | 'ERRO';

export const NewExecution: React.FC = () => {
  const [despesas, setDespesas] = useState<File | null>(null);
  const [razao, setRazao] = useState<File | null>(null);
  const [extrato, setExtrato] = useState<File | null>(null);
  
  const [standardFile, setStandardFile] = useState<File | null>(null);
  const [status, setStatus] = useState<FormState>('IDLE');
  const [errorMsg, setErrorMsg] = useState('');
  
  const navigate = useNavigate();

  const handleDownloadStandard = () => {
    window.open(`${api.defaults.baseURL}/templates/standard`, '_blank');
  };

  const handleStandardSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!standardFile) {
      setErrorMsg('Por favor, selecione o arquivo da Planilha Padrão.');
      return;
    }

    try {
      setStatus('LOADING');
      setErrorMsg('');

      const res = await api.post('/executions');
      const execution = res.data;

      const formData = new FormData();
      formData.append('file', standardFile);
      await api.post(`/executions/${execution.id}/import-standard`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setStatus('CONCLUIDO');
      navigate(`/executions/${execution.id}/staging`);

    } catch (err: any) {
      console.error(err);
      setStatus('ERRO');
      setErrorMsg('Ocorreu um erro durante a importação da planilha padrão.');
    }
  };

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
      await api.post(`/executions/${execution.id}/files`, formData, {
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

  const FileDropzone = ({ label, file, onChange, disabled }: { label: string, file: File | null, onChange: any, disabled: boolean }) => (
    <div className="relative overflow-hidden group">
      <div className={`
        border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200
        ${file ? 'border-primary-400 bg-primary-50/10 dark:bg-primary-900/10' : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 hover:bg-gray-50/50 dark:hover:bg-gray-800/50'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}>
        <input 
          type="file" 
          accept=".xlsx,.csv" 
          onChange={onChange} 
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed" 
        />
        
        <div className="flex flex-col items-center justify-center space-y-3 pointer-events-none">
          {file ? (
            <>
              <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400">
                <FileSpreadsheet className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <p className="font-medium text-gray-900 dark:text-gray-100">{label}</p>
                <p className="text-sm text-primary-600 dark:text-primary-400 truncate max-w-[250px]">{file.name}</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-500 dark:text-gray-400 group-hover:scale-110 transition-transform">
                <FileUp className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <p className="font-medium text-gray-700 dark:text-gray-300">{label}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Clique ou arraste um arquivo .xlsx</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Breadcrumb items={[{ label: 'Execuções', href: '/executions' }, { label: 'Nova Conciliação' }]} />
      <PageHeader title="Nova Conciliação" description="Inicie um novo processo de conciliação enviando os arquivos base." />

      <GlassPanel className="p-8 space-y-6">
        <div className="bg-primary-50/50 dark:bg-primary-950/30 border border-primary-200 dark:border-primary-800/50 rounded-xl p-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-primary-900 dark:text-primary-100">Modelo Padrão do Sistema (Recomendado)</h3>
            <p className="text-sm text-primary-700 dark:text-primary-300">Baixe o modelo `.xlsx` padronizado com abas de Receitas, Despesas, Extrato e Dinheiro para editar e revisar no Staging.</p>
          </div>
          <Button onClick={handleDownloadStandard} variant="outline" className="shrink-0">
            Baixar Modelo Padrão .xlsx
          </Button>
        </div>

        {status === 'ERRO' && (
          <div className="p-4 bg-destructive/10 text-destructive border border-destructive/20 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5" />
            <p className="font-medium">{errorMsg}</p>
          </div>
        )}
        
        {status === 'CONCLUIDO' && (
          <div className="p-4 bg-green-50 dark:bg-green-500/10 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-500/20 rounded-lg flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5" />
            <p className="font-medium">Importação concluída! Redirecionando para a área de revisão...</p>
          </div>
        )}

        <form onSubmit={handleStandardSubmit} className="space-y-4 pt-2 border-b border-gray-200 dark:border-gray-700/50 pb-6">
          <h4 className="font-medium text-gray-900 dark:text-gray-100">Envio da Planilha Padrão Integrada</h4>
          <FileDropzone 
            label="Planilha Padrão (.xlsx)" 
            file={standardFile} 
            onChange={handleFileChange(setStandardFile)} 
            disabled={status !== 'IDLE' && status !== 'ERRO'} 
          />
          <div className="flex justify-end">
            <Button type="submit" isLoading={status === 'LOADING'} disabled={!standardFile}>
              Carregar no Staging CRUD
            </Button>
          </div>
        </form>

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
          <h4 className="font-medium text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wider">Ou envie os arquivos legados separados</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <FileDropzone 
              label="Despesas (ERP)" 
              file={despesas} 
              onChange={handleFileChange(setDespesas)} 
              disabled={status !== 'IDLE' && status !== 'ERRO'} 
            />
            <FileDropzone 
              label="Razão Contábil" 
              file={razao} 
              onChange={handleFileChange(setRazao)} 
              disabled={status !== 'IDLE' && status !== 'ERRO'} 
            />
            <FileDropzone 
              label="Extrato Bancário" 
              file={extrato} 
              onChange={handleFileChange(setExtrato)} 
              disabled={status !== 'IDLE' && status !== 'ERRO'} 
            />
          </div>

          <div className="pt-6 border-t border-gray-200 dark:border-gray-700/50 flex justify-end">
            <Button 
              type="submit" 
              size="lg"
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
