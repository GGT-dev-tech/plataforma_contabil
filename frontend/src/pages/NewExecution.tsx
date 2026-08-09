import React, { useState } from 'react';
import { apiClient as api } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { Button } from '../components/ui/Button';
import { GlassPanel } from '../components/ui/GlassPanel';
import { PageHeader } from '../components/layout/PageHeader';
import { Breadcrumb } from '../components/layout/Breadcrumb';
import { FileUp, FileSpreadsheet, FileText, FileCode, AlertCircle, CheckCircle2 } from 'lucide-react';

type FormState = 'IDLE' | 'LOADING' | 'PROCESSANDO' | 'CONCLUIDO' | 'ERRO';

export const NewExecution: React.FC = () => {
  const [despesas, setDespesas] = useState<File | null>(null);
  const [razao, setRazao] = useState<File | null>(null);
  const [extrato, setExtrato] = useState<File | null>(null);
  
  const [status, setStatus] = useState<FormState>('IDLE');
  const [errorMsg, setErrorMsg] = useState('');
  
  const { activeWorkspaceId } = useWorkspace();
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
      const res = await api.post('/executions', {
        empresa_id: activeWorkspaceId
      });
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
      // Navigate to Staging Preview for Semantic Validation
      setTimeout(() => navigate(`/executions/${execution.id}/staging`), 1500);
      
    } catch (err: any) {
      console.error(err);
      setStatus('ERRO');
      setErrorMsg('Ocorreu um erro durante a criação da execução.');
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf': return <FileText className="w-6 h-6 text-red-500" />;
      case 'xml': return <FileCode className="w-6 h-6 text-orange-500" />;
      case 'csv': return <FileText className="w-6 h-6 text-emerald-500" />;
      case 'xlsx': return <FileSpreadsheet className="w-6 h-6 text-green-600" />;
      default: return <FileUp className="w-6 h-6" />;
    }
  };

  const getFileFormatBadge = (filename: string) => {
    const ext = filename.split('.').pop()?.toUpperCase();
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 mt-1">
        Formato: {ext || 'Desconhecido'}
      </span>
    );
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
          accept=".xlsx,.csv,.pdf,.xml" 
          onChange={onChange} 
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed" 
        />
        
        <div className="flex flex-col items-center justify-center space-y-3 pointer-events-none">
          {file ? (
            <>
              <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                {getFileIcon(file.name)}
              </div>
              <div className="space-y-1">
                <p className="font-medium text-gray-900 dark:text-gray-100">{label}</p>
                <p className="text-sm text-primary-600 dark:text-primary-400 truncate max-w-[250px]">{file.name}</p>
                {getFileFormatBadge(file.name)}
              </div>
            </>
          ) : (
            <>
              <div className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-500 dark:text-gray-400 group-hover:scale-110 transition-transform">
                <FileUp className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <p className="font-medium text-gray-700 dark:text-gray-300">{label}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Arraste: PDF, XML, CSV, XLSX</p>
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
        {status === 'ERRO' && (
          <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5" />
            <p className="font-medium">{errorMsg}</p>
          </div>
        )}
        
        {status === 'CONCLUIDO' && (
          <div className="p-4 bg-green-50 text-green-700 border border-green-200 rounded-lg flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5" />
            <p className="font-medium">Upload concluído! A conciliação foi agendada assincronamente. Redirecionando...</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
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
