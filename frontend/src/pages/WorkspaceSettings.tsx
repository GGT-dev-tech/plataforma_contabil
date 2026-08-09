import React, { useState, useEffect } from 'react';
import { useWorkspace } from '../contexts/WorkspaceContext';
import { apiClient as api } from '../services/api';
import { Save, FileSpreadsheet, Settings } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const WorkspaceSettings: React.FC = () => {
  const { activeWorkspace, activeWorkspaceId } = useWorkspace();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const [despesaConfig, setDespesaConfig] = useState({
    col_data: 'Data Vencimento',
    col_valor: 'Valor Parcela',
    col_descricao: 'ID',
    col_entidade: 'Fornecedor',
    skip_rows: 0,
  });

  useEffect(() => {
    if (activeWorkspace?.import_config?.DESPESA) {
      setDespesaConfig(activeWorkspace.import_config.DESPESA);
    }
  }, [activeWorkspace]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setDespesaConfig(prev => ({
      ...prev,
      [name]: type === 'number' ? parseInt(value) || 0 : value
    }));
  };

  const handleSave = async () => {
    if (!activeWorkspaceId) return;
    
    setLoading(true);
    setMessage(null);
    try {
      const payload = {
        ...(activeWorkspace?.import_config || {}),
        DESPESA: despesaConfig
      };
      
      await api.put(`/workspaces/empresas/${activeWorkspaceId}/import-config`, payload);
      
      // Update local context manually or reload (we'll just show success here)
      setMessage({ type: 'success', text: 'Configurações de importação atualizadas com sucesso!' });
      
      // We could ideally trigger a context refresh here, but reloading window works for now
      setTimeout(() => window.location.reload(), 1500);
    } catch (err) {
      console.error(err);
      setMessage({ type: 'error', text: 'Erro ao salvar configurações.' });
    } finally {
      setLoading(false);
    }
  };

  if (!activeWorkspaceId) {
    return <div className="p-8">Selecione uma empresa para configurar.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent mb-2">
            Configurações do Workspace
          </h1>
          <p className="text-gray-400">
            Configure as regras de negócio e de importação para a empresa: <strong className="text-primary-400">{activeWorkspace?.nome_fantasia}</strong>
          </p>
        </div>
        <div className="w-12 h-12 rounded-xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
          <Settings className="w-6 h-6 text-primary-400" />
        </div>
      </div>

      <div className="glass-panel p-8 rounded-2xl border border-white/5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/5 rounded-full filter blur-[80px] -z-10 pointer-events-none"></div>
        
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center border border-green-500/20">
            <FileSpreadsheet className="w-5 h-5 text-green-400" />
          </div>
          <h2 className="text-xl font-semibold text-white">Importação de Despesas (Excel/CSV)</h2>
        </div>
        
        <p className="text-gray-400 mb-6 text-sm">
          Mapeie exatamente o nome das colunas que vêm na planilha do seu cliente para que o sistema consiga extrair os dados sem falhas.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Coluna de Data de Vencimento *</label>
            <input 
              type="text" 
              name="col_data"
              value={despesaConfig.col_data}
              onChange={handleChange}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all"
              placeholder="Ex: Vencimento Parcela"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Coluna de Valor *</label>
            <input 
              type="text" 
              name="col_valor"
              value={despesaConfig.col_valor}
              onChange={handleChange}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all"
              placeholder="Ex: Valor Parcela"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Coluna de Descrição / N° Documento</label>
            <input 
              type="text" 
              name="col_descricao"
              value={despesaConfig.col_descricao}
              onChange={handleChange}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all"
              placeholder="Ex: ID Parcela"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Coluna de Fornecedor / Entidade</label>
            <input 
              type="text" 
              name="col_entidade"
              value={despesaConfig.col_entidade}
              onChange={handleChange}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all"
              placeholder="Ex: Nome do Fornecedor"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">Linhas a ignorar no cabeçalho (Skip Rows)</label>
            <input 
              type="number" 
              name="skip_rows"
              value={despesaConfig.skip_rows}
              onChange={handleChange}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all"
            />
          </div>
        </div>
        
        {message && (
          <div className={`mt-6 p-4 rounded-xl text-sm ${message.type === 'success' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
            {message.text}
          </div>
        )}

        <div className="mt-8 flex justify-end">
          <Button onClick={handleSave} disabled={loading} variant="default" leftIcon={<Save className="w-4 h-4" />}>
            {loading ? 'Salvando...' : 'Salvar Configurações'}
          </Button>
        </div>
      </div>
    </div>
  );
};
