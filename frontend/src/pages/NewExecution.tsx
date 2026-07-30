import React, { useState } from 'react';
import { executionsApi } from '../api/executions';
import { useNavigate } from 'react-router-dom';

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
      const execution = await executionsApi.create();

      // 2. Upload Files
      await executionsApi.uploadFiles(execution.id, despesas, razao, extrato);

      // 3. Start Run
      setStatus('PROCESSANDO');
      await executionsApi.run(execution.id);
      
      setStatus('CONCLUIDO');
      
      // Navigate to candidates view (human in the loop) after a short delay
      setTimeout(() => navigate('/candidates'), 1500);
      
    } catch (err: any) {
      console.error(err);
      setStatus('ERRO');
      setErrorMsg('Ocorreu um erro durante a criação da execução.');
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', backgroundColor: 'white', padding: '2rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>Nova Conciliação</h2>
      
      {status === 'ERRO' && (
        <div style={{ padding: '1rem', backgroundColor: '#fee2e2', color: '#b91c1c', borderRadius: '4px', marginBottom: '1rem' }}>
          {errorMsg}
        </div>
      )}
      
      {status === 'CONCLUIDO' && (
        <div style={{ padding: '1rem', backgroundColor: '#dcfce7', color: '#15803d', borderRadius: '4px', marginBottom: '1rem' }}>
          Pipeline iniciada com sucesso! Redirecionando para revisão...
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        <div style={{ border: '2px dashed #d1d5db', padding: '2rem', borderRadius: '8px', textAlign: 'center' }}>
          <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Arquivo de Despesas (XLSX/CSV)</label>
          <input type="file" accept=".xlsx,.csv" onChange={handleFileChange(setDespesas)} disabled={status !== 'IDLE' && status !== 'ERRO'} />
          {despesas && <p style={{ marginTop: '0.5rem', color: '#4b5563' }}>Selecionado: {despesas.name}</p>}
        </div>

        <div style={{ border: '2px dashed #d1d5db', padding: '2rem', borderRadius: '8px', textAlign: 'center' }}>
          <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Arquivo de Razão (XLSX/CSV)</label>
          <input type="file" accept=".xlsx,.csv" onChange={handleFileChange(setRazao)} disabled={status !== 'IDLE' && status !== 'ERRO'} />
          {razao && <p style={{ marginTop: '0.5rem', color: '#4b5563' }}>Selecionado: {razao.name}</p>}
        </div>

        <div style={{ border: '2px dashed #d1d5db', padding: '2rem', borderRadius: '8px', textAlign: 'center' }}>
          <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Arquivo de Extrato (XLSX/CSV)</label>
          <input type="file" accept=".xlsx,.csv" onChange={handleFileChange(setExtrato)} disabled={status !== 'IDLE' && status !== 'ERRO'} />
          {extrato && <p style={{ marginTop: '0.5rem', color: '#4b5563' }}>Selecionado: {extrato.name}</p>}
        </div>

        <button 
          type="submit" 
          disabled={status === 'LOADING' || status === 'PROCESSANDO' || status === 'CONCLUIDO'}
          style={{
            padding: '1rem',
            backgroundColor: (status === 'LOADING' || status === 'PROCESSANDO' || status === 'CONCLUIDO') ? '#9ca3af' : '#2563eb',
            color: 'white',
            fontWeight: 'bold',
            border: 'none',
            borderRadius: '4px',
            cursor: (status === 'LOADING' || status === 'PROCESSANDO' || status === 'CONCLUIDO') ? 'not-allowed' : 'pointer'
          }}
        >
          {status === 'IDLE' && 'Iniciar Conciliação'}
          {status === 'LOADING' && 'Enviando Arquivos...'}
          {status === 'PROCESSANDO' && 'Iniciando Pipeline...'}
          {status === 'CONCLUIDO' && 'Concluído'}
          {status === 'ERRO' && 'Tentar Novamente'}
        </button>

      </form>
    </div>
  );
};
