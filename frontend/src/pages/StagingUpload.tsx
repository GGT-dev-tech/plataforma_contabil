import React, { useState } from 'react';
import { apiClient as api } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { PageHeader } from '../components/layout/PageHeader';
import { Breadcrumb } from '../components/layout/Breadcrumb';
import { FileUp, FileSpreadsheet, FileText, FileCode, AlertCircle, CheckCircle2 } from 'lucide-react';

type FormState = 'IDLE' | 'LOADING' | 'PROCESSANDO' | 'CONCLUIDO' | 'ERRO';

export const StagingUpload: React.FC = () => {
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
      case 'pdf': return <FileText className="w-8 h-8 text-red-400 drop-shadow-md" />;
      case 'xml': return <FileCode className="w-8 h-8 text-orange-400 drop-shadow-md" />;
      case 'csv': return <FileText className="w-8 h-8 text-emerald-400 drop-shadow-md" />;
      case 'xlsx': return <FileSpreadsheet className="w-8 h-8 text-emerald-500 drop-shadow-md" />;
      default: return <FileUp className="w-8 h-8 text-primary-400 drop-shadow-md" />;
    }
  };

  const FileDropzone = ({ label, file, onChange, disabled }: { label: string, file: File | null, onChange: any, disabled: boolean }) => (
    <div className="relative overflow-hidden group h-64 rounded-2xl">
      <div className={`
        absolute inset-0 border-2 border-dashed rounded-xl p-6 text-center transition-all duration-300 flex flex-col items-center justify-center
        ${file ? 'border-primary-600/50 bg-primary-50' : 'border-slate-300 hover:border-primary-500 hover:bg-slate-50'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}>
        <input 
          type="file" 
          accept=".xlsx,.csv,.pdf,.xml" 
          onChange={onChange} 
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed z-10" 
        />
        
        {/* Animated Dashed Border Effect (CSS Only Trick) */}
        {!file && !disabled && (
          <div className="absolute inset-0 rounded-xl pointer-events-none border-2 border-transparent group-hover:border-primary-300 transition-all"></div>
        )}
        
        <div className="flex flex-col items-center justify-center space-y-4 pointer-events-none relative z-0">
          {file ? (
            <>
              <div className="w-16 h-16 rounded-xl bg-white border border-slate-200 flex items-center justify-center shadow-sm">
                {getFileIcon(file.name)}
              </div>
              <div className="space-y-2">
                <p className="font-bold text-slate-800 tracking-wide">{label}</p>
                <p className="text-sm text-primary-700 truncate max-w-[200px] font-medium">{file.name}</p>
              </div>
            </>
          ) : (
            <>
              <div className="w-16 h-16 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400 group-hover:scale-110 group-hover:bg-primary-100 transition-all duration-300">
                <FileUp className="w-8 h-8 group-hover:text-primary-600" />
              </div>
              <div className="space-y-1">
                <p className="font-bold text-slate-700 tracking-wide group-hover:text-primary-700 transition-colors">{label}</p>
                <p className="text-xs text-slate-500 uppercase tracking-wider font-medium">Arraste um Arquivo</p>
                <p className="text-xs text-slate-400">PDF, XML, CSV, XLSX</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <Breadcrumb items={[{ label: 'Importação', href: '/executions' }, { label: 'Upload de Arquivos' }]} />
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Central de Upload</h1>
        <p className="text-slate-500">Inicie um novo processo de ingestão enviando os arquivos base (Razão, Extrato e Despesas).</p>
      </div>

      <div className="bg-white rounded-xl p-8 border border-slate-200 shadow-sm">
        {status === 'ERRO' && (
          <div className="mb-6 p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5" />
            <p className="font-medium">{errorMsg}</p>
          </div>
        )}
        
        {status === 'CONCLUIDO' && (
          <div className="mb-6 p-4 bg-green-50 text-green-700 border border-green-200 rounded-lg flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5" />
            <p className="font-medium">Upload concluído! A conciliação foi iniciada. Redirecionando...</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
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

          <div className="pt-8 border-t border-slate-100 flex justify-end">
            <button 
              type="submit" 
              disabled={status === 'LOADING' || status === 'PROCESSANDO' || status === 'CONCLUIDO'}
              className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-lg text-sm font-semibold tracking-wide disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {status === 'IDLE' && 'Iniciar Inteligência Contábil'}
              {status === 'LOADING' && 'Enviando Arquivos...'}
              {status === 'PROCESSANDO' && 'Iniciando Pipeline...'}
              {status === 'CONCLUIDO' && 'Concluído'}
              {status === 'ERRO' && 'Tentar Novamente'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
